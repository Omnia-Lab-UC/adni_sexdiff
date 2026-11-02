"""The report's figures (change ``adni-report-figures``): their data rows and their SVGs.

``report`` draws the nine figures of ``REPORT_FIGURES`` after every gate,
from the inputs ``_load_report_inputs`` returned and checked, and reads no
other file. Each figure is a data CSV and an SVG:

- the data CSV holds one row per plotted value, in drawing order: ``key``
  (unique within the figure, its coordinates ``|``-joined), ``quantity``,
  ``value`` (the source value as read: a CSV cell unchanged, a JSON number by
  its shortest round trip, a JSON string unchanged, ``absent`` for a cell
  ``stage_counts.csv`` does not list), ``source`` (the input path, or
  ``constants.<NAME>`` for a reference line) and ``field`` (a JSON path, or a
  CSV row key and column, or for ``absent`` the key looked up);
- the SVG is drawn from those rows only, so the data CSV records every value
  the figure shows. Every number printed in a figure is its row value at the
  digits the report prints for it, through the report's formatters; no
  figure computes a statistic, correlation, mean or count.

The SVG is drawn on ``matplotlib.figure.Figure`` with the SVG canvas, never
``pyplot``, inside ``rc_context`` on ``rcParamsDefault`` updated with
``FIGURE_STYLE``, with matplotlib's font list restricted to the bundled
DejaVu Sans files ``FIGURE_STYLE`` names, so a user's ``matplotlibrc`` or a
system font cannot move the bytes. Its metadata names the figure's title,
each input with its sha256 and the matplotlib version, and carries no date.
This module is the only one that imports matplotlib; ``data.py`` imports it
inside ``run_report`` and ``check_report`` only, so no pipeline step loads it.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import math
from collections.abc import Callable, Generator
from pathlib import Path

import matplotlib
import numpy as np
from matplotlib import font_manager
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from . import constants
from .constants import (
    ANALYSIS_COVARIATES,
    ANALYSIS_STATISTICS,
    EXPORT_BLOCKS,
    EXPORT_VARIANT_RULE_SETS,
    FIGURE_STYLE,
    LATENT_SENSITIVITY_ARM,
    MATPLOTLIB_VERSION,
    REPORT_EXPORT_VARIANTS,
    REPORT_FIGURES,
    STAGE_RULE,
    STAGE_SENSITIVITY_ARM,
)
from .data import _count, _fmt, _num

#: The columns of every figure's data CSV (design D4).
FIGURE_CSV_COLUMNS: tuple[str, ...] = ("key", "quantity", "value", "source", "field")
#: The value of a data row whose cell ``stage_counts.csv`` does not list.
ABSENT = "absent"
#: The ``stage_counts.csv`` set of the analysis cohort.
_INTERSECTION = "intersection"
#: The title of each statistic's panel.
_STAT_TITLE = {"delta": "delta", "angle": "angle (degrees, CN → AD)", "shape": "shape"}

_PAL = FIGURE_STYLE["palette"]


# --- the data rows -----------------------------------------------------------------


def _json_value(value) -> str:
    """A JSON value as the data CSV records it: a number by its shortest round trip, a string unchanged."""
    if isinstance(value, bool) or value is None:
        return json.dumps(value)
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return value
    raise TypeError(f"a figure plots scalars only, not {type(value).__name__}")


def _csv_field(where: dict[str, str], column: str | None) -> str:
    """A CSV row key and column as the ``field`` of a data row (``a=x,b=y:column``)."""
    key = ",".join(f"{k}={v}" for k, v in where.items())
    return key if column is None else f"{key}:{column}"


class _Rows:
    """The rows of one figure's data CSV, in drawing order; every key once."""

    def __init__(self, figure: str, inputs: dict) -> None:
        self.figure, self.files = figure, inputs["files"]
        self.rows: list[dict[str, str]] = []
        self._keys: set[str] = set()

    def path(self, role: str, name: str) -> str:
        return str(self.files[role][name]["path"])

    def add(self, key: str, quantity: str, value: str, source: str, field: str) -> None:
        if key in self._keys:
            raise RuntimeError(f"{self.figure}: the data row {key!r} is built twice (the figure's rows are defective)")
        self._keys.add(key)
        self.rows.append({"key": key, "quantity": quantity, "value": value, "source": source, "field": field})

    def cell(
        self, key: str, quantity: str, role: str, name: str, frame, where: dict[str, str], column: str,
        *, absent_ok: bool = False,
    ) -> None:
        """The cell of the one row of ``frame`` that matches ``where``; ``absent`` when none does and ``absent_ok``."""
        match = frame
        for k, v in where.items():
            match = match[match[k] == v]
        if len(match) > 1 or (len(match) == 0 and not absent_ok):
            raise RuntimeError(
                f"{self.figure}: {self.path(role, name)} holds {len(match)} rows {_csv_field(where, None)} (one expected); "
                "nothing was written"
            )
        if len(match) == 0:
            self.add(key, quantity, ABSENT, self.path(role, name), _csv_field(where, None))
            return
        self.add(key, quantity, str(match.iloc[0][column]), self.path(role, name), _csv_field(where, column))

    def json(self, key: str, quantity: str, role: str, name: str, document: dict, field: str) -> None:
        """The value at ``field`` (a dotted JSON path; a list item by its index) of a parsed JSON input."""
        node = document
        for part in field.split("."):
            node = node[int(part)] if isinstance(node, list) else node[part]
        self.add(key, quantity, _json_value(node), self.path(role, name), field)

    def constant(self, key: str, quantity: str, name: str) -> None:
        """A reference line: a named constant of ``constants.py``."""
        self.add(key, quantity, _json_value(getattr(constants, name)), f"constants.{name}", name)


def _inputs(stem: str) -> tuple[tuple[str, str], ...]:
    return REPORT_FIGURES[stem]["inputs"]


def _record(inputs: dict, role: str, name: str) -> dict:
    """A JSON input parsed from the bytes the gates hashed."""
    return json.loads(Path(inputs["files"][role][name]["path"]).read_text())


def _rows_cohort(r: _Rows, inputs: dict) -> None:
    ((role, name),) = _inputs("f1_cohort_design")
    frame = inputs["tables"]["stage_counts"]
    for sex in constants.GROUP_VALUES:
        r.cell(f"{sex}|all", "participants of the sex", role, name, frame,
               {"set": _INTERSECTION, "sex": sex, "stage": "all", "dx_bl": "all", "phase": "all"}, "n")
        for dx, stage in STAGE_RULE["map"].items():
            for phase in ANALYSIS_COVARIATES["phase"]["levels"]:
                r.cell(f"{sex}|{dx}|{phase}", "participants", role, name, frame,
                       {"set": _INTERSECTION, "sex": sex, "stage": stage, "dx_bl": dx, "phase": phase}, "n",
                       absent_ok=True)


def _rows_trajectories(r: _Rows, inputs: dict) -> None:
    (m_role, m_name), (a_role, a_name), (g_role, g_name), (x_role, x_name) = _inputs("f2_trajectories")
    record = inputs["records"]["primary"]
    means = inputs["tables"]["stage_means"]
    geometry, axis = inputs["tables"]["diagnostics"]["geometry"], inputs["tables"]["diagnostics"]["axis"]
    components = [c for c in means.columns if c.startswith("pls_")]
    groups, stages = record["design"]["group_levels"], record["design"]["stage_levels"]
    r.json("rank", "CV-selected rank", a_role, a_name, record, "latent.selected_lv")
    r.constant("threshold", "reporting flag on |rho|", "DIAGNOSTIC_CORRELATION_THRESHOLD")
    for component in components:
        r.cell(f"{component}|share", "share of the summed squared sex differences across stages",
               g_role, g_name, geometry, {"quantity": "sex_difference_by_stage", "component": component}, "share")
        flagged = axis[(axis["component"] == component) & ((axis["flag_raw"] == "True") | (axis["flag_partial"] == "True"))]
        for variable in flagged["variable"]:
            where = {"component": component, "variable": variable}
            r.cell(f"{component}|flag|{variable}|spearman", "Spearman rho, flagged", x_role, x_name, axis, where,
                   "spearman")
            if flagged[flagged["variable"] == variable].iloc[0]["flag_partial"] == "True":
                r.cell(f"{component}|flag|{variable}|partial_spearman", "partial Spearman rho given the design, flagged",
                       x_role, x_name, axis, where, "partial_spearman")
        for group in groups:
            for stage in stages:
                r.cell(f"{group}|{stage}|{component}", "covariate-adjusted stage mean (LS-mean latent score)", m_role,
                       m_name, means, {"group": group, "stage": stage}, component)


def _rows_primary_tests(r: _Rows, inputs: dict) -> None:
    (a_role, a_name), (d_role, d_name) = _inputs("f3_primary_tests")
    record, decision = inputs["records"]["primary"], inputs["decision"]
    r.constant("alpha", "ANALYSIS_ALPHA", "ANALYSIS_ALPHA")
    for s in ANALYSIS_STATISTICS:
        for q in ("q50", "q95", "q99"):
            r.json(f"{s}|null_{q}", f"RRPP null {q}", a_role, a_name, record, f"null_summary.{s}.{q}")
        r.json(f"{s}|observed", "observed statistic", a_role, a_name, record, f"statistics.{s}")
        r.json(f"{s}|p", "RRPP p-value", a_role, a_name, record, f"p_values.{s}")
        r.json(f"{s}|max_rate", "highest rejection rate measured at this design", d_role, d_name, decision,
               f"power.{s}.max_rate")
        r.json(f"{s}|floor", "power floor of the decision", d_role, d_name, decision, f"power.{s}.floor")


def _rows_operating_characteristics(r: _Rows, inputs: dict) -> None:
    ((role, name),) = _inputs("f4_operating_characteristics")
    decision = inputs["decision"]
    r.json("size|alpha", "the decision's alpha", role, name, decision, "rule.alpha")
    r.json("size|bound", "one-sided bound of the size readings", role, name, decision, "size.readings.0.bound")
    for k, reading in enumerate(decision["size"]["readings"]):
        key = f"size|{reading['mode']}|{reading['statistic']}"
        r.json(f"{key}|rate", "rejection rate with no effect", role, name, decision, f"size.readings.{k}.rate")
        r.json(f"{key}|monte_carlo_se", "Monte Carlo standard error", role, name, decision,
               f"size.readings.{k}.monte_carlo_se")
    for s in ANALYSIS_STATISTICS:
        r.json(f"power|{s}|mode", "construction", role, name, decision, f"power.{s}.mode")
        r.json(f"power|{s}|floor", "power floor", role, name, decision, f"power.{s}.floor")
        for k, _ in enumerate(decision["power"][s]["effects"]):
            for field, quantity in (("effect", "injected effect"), ("rate", "rejection rate"),
                                    ("monte_carlo_se", "Monte Carlo standard error")):
                r.json(f"power|{s}|e{k}|{field}", quantity, role, name, decision, f"power.{s}.effects.{k}.{field}")
        r.json(f"power|{s}|max_rate", "highest rejection rate", role, name, decision, f"power.{s}.max_rate")
        r.json(f"power|{s}|effect_at_max", "effect at the highest rate", role, name, decision, f"power.{s}.effect_at_max")


def _rows_axis_diagnostics(r: _Rows, inputs: dict) -> None:
    (x_role, x_name), (c_role, c_name), (e_role, e_name) = _inputs("f5_axis_diagnostics")
    axis, components = inputs["tables"]["diagnostics"]["axis"], inputs["tables"]["diagnostics"]["components"]
    r.constant("threshold", "reporting flag on |rho|", "DIAGNOSTIC_CORRELATION_THRESHOLD")
    for component in dict.fromkeys(axis["component"]):
        for variable in axis[axis["component"] == component]["variable"]:
            where = {"component": component, "variable": variable}
            for column, quantity in (("spearman", "Spearman rho"), ("partial_spearman", "partial Spearman rho given the design"),
                                     ("flag_raw", "flag on the raw rho"), ("flag_partial", "flag on the partial rho")):
                r.cell(f"{component}|{variable}|{column}", quantity, x_role, x_name, axis, where, column)
        for block in EXPORT_BLOCKS:
            r.cell(f"{component}|loading_share_{block}", f"loading share of the {block} block", c_role, c_name, components,
                   {"component": component}, f"loading_share_{block}")
    r.json("feature_share|p180", "p180 share of the joint features", e_role, e_name, inputs["manifests"]["export"],
           "counts.block_shares.p180")


def _export_names() -> list[str]:
    """The exports of ``f6_block_phase``, in its row order: the primary, the variants, the CN / LMCI / AD arm."""
    return ["primary", *REPORT_EXPORT_VARIANTS, STAGE_SENSITIVITY_ARM["name"]]


def _rows_block_phase(r: _Rows, inputs: dict) -> None:
    tables = inputs["tables"]
    frames = [tables["diagnostics"]["block_pcs"], *(tables["variants"][v]["diagnostics"]["block_pcs"] for v in REPORT_EXPORT_VARIANTS),
              tables["stage_arm"]["diagnostics"]["block_pcs"]]
    r.constant("threshold", "reporting flag on |rho|", "DIAGNOSTIC_CORRELATION_THRESHOLD")
    for export, frame, (role, name) in zip(_export_names(), frames, _inputs("f6_block_phase"), strict=True):
        for block in EXPORT_BLOCKS:
            rows = frame[(frame["block"] == block) & (frame["variable"] == "phase")]
            for component in rows["component"]:
                r.cell(f"{export}|{block}|{component}", "Spearman rho of the block PC with phase", role, name, frame,
                       {"block": block, "component": component, "variable": "phase"}, "spearman")


def _rows_nist_bridge(r: _Rows, inputs: dict) -> None:
    (b_role, b_name), (e_role, e_name) = _inputs("f7_nist_bridge")
    variant = b_role.split("/")[1]
    table, manifest = inputs["tables"]["variants"][variant]["bridge"], _record(inputs, e_role, e_name)
    r.json("legend|metabolites", "p180 metabolites of the bridge", e_role, e_name, manifest, "bridge.summary.metabolites")
    for kit in ("FIA", "UPLC", "not_bridged"):
        r.json(f"legend|{kit}", "metabolites bridged per kit" if kit != "not_bridged" else "metabolites not bridged",
               e_role, e_name, manifest, f"bridge.summary.p180_bridged.{kit}")
    order = sorted(range(len(table)), key=lambda i: float(table.iloc[i]["b"]))
    for i in order:
        metabolite = table.iloc[i]["metabolite"]
        where = {"metabolite": metabolite}
        for column, quantity in (("b", "bridge factor b (log2)"), ("se_b", "plate-clustered SE of b"),
                                 ("bridged", "bridged"), ("kit", "kit")):
            r.cell(f"{metabolite}|{column}", quantity, b_role, b_name, table, where, column)
        if table.iloc[i]["bridged"] != "True":
            r.cell(f"{metabolite}|nist_column", "NIST column (label)", b_role, b_name, table, where, "nist_column")


def _sensitivity_rows() -> list[tuple[str, str, int]]:
    """The rows of ``f8_sensitivities``, in figure order: (name, rule list, index of its comparison table in the inputs).

    The comparison's manifest follows its table in ``REPORT_FIGURES["f8_sensitivities"]["inputs"]``.
    """
    out = [(LATENT_SENSITIVITY_ARM["name"], "LATENT_SENSITIVITY_READING_RULES", 0)]
    out += [(v, EXPORT_VARIANT_RULE_SETS[v]["rules"], 2 + 2 * k) for k, v in enumerate(REPORT_EXPORT_VARIANTS)]
    stage_at = 2 + 2 * len(REPORT_EXPORT_VARIANTS)
    out.append((STAGE_SENSITIVITY_ARM["name"], "STAGE_SENSITIVITY_READING_RULES", stage_at))
    out += [
        (constants.RANK_SENSITIVITY_RANK_DIR.format(rank=int(k)), "RANK_SENSITIVITY_READING_RULES", stage_at + 2)
        for k in constants.RANK_SENSITIVITY_LADDER["ranks"]
    ]
    return out


def _rule_set_of(name: str) -> str:
    return next(rules for n, rules, _ in _sensitivity_rows() if n == name)


def _rows_sensitivities(r: _Rows, inputs: dict) -> None:
    entries = _inputs("f8_sensitivities")
    tables = inputs["tables"]
    frames = {
        0: tables["comparison"],
        **{2 + 2 * k: tables["variants"][v]["comparison"] for k, v in enumerate(REPORT_EXPORT_VARIANTS)},
        2 + 2 * len(REPORT_EXPORT_VARIANTS): tables["stage_arm"]["comparison"],
        4 + 2 * len(REPORT_EXPORT_VARIANTS): tables["rank_sweep"]["comparison"],
    }
    r.constant("alpha", "ANALYSIS_ALPHA", "ANALYSIS_ALPHA")
    t_role, t_name = entries[0]
    for s in ANALYSIS_STATISTICS:
        for column in (f"{s}_p", f"{s}_rejected"):
            r.cell(f"primary|{s}|{column.removeprefix(s + '_')}", "the primary's RRPP p-value" if column.endswith("_p")
                   else "the primary's rejection", t_role, t_name, frames[0], {"analysis": "primary"}, column)
    for name, _, at in _sensitivity_rows():
        (t_role, t_name), (m_role, m_name) = entries[at], entries[at + 1]
        frame, manifest = frames[at], _record(inputs, m_role, m_name)
        where = {"analysis": name}
        r.cell(f"{name}|selected_rank", "rank", t_role, t_name, frame, where, "selected_rank")
        for s in ANALYSIS_STATISTICS:
            r.cell(f"{name}|{s}|p", "RRPP p-value", t_role, t_name, frame, where, f"{s}_p")
            r.cell(f"{name}|{s}|rejected", "rejected under ANALYSIS_REJECTION_RULE", t_role, t_name, frame, where,
                   f"{s}_rejected")
            field = f"counts.statuses.{name}.{s}" if name.startswith("rank_") else f"counts.statuses.{s}"
            r.json(f"{name}|{s}|status", "status against the primary", m_role, m_name, manifest, field)


def _rows_rank_sweep(r: _Rows, inputs: dict) -> None:
    entries = _inputs("f9_rank_sweep")
    records = [("primary", inputs["records"]["primary"], entries[0])]
    records += [
        (constants.RANK_SENSITIVITY_RANK_DIR.format(rank=int(k)), inputs["records"]["ranks"][int(k)], entries[1 + j])
        for j, k in enumerate(constants.RANK_SENSITIVITY_LADDER["ranks"])
    ]
    records.sort(key=lambda t: t[1]["latent"]["selected_lv"])
    for name, record, (role, file) in records:
        r.json(f"{name}|rank", "PLS-DA rank", role, file, record, "latent.selected_lv")
        for s in ANALYSIS_STATISTICS:
            for q in ("q50", "q95", "q99"):
                r.json(f"{name}|{s}|null_{q}", f"RRPP null {q}", role, file, record, f"null_summary.{s}.{q}")
            r.json(f"{name}|{s}|observed", "observed statistic", role, file, record, f"statistics.{s}")


_ROW_BUILDERS: dict[str, Callable[[_Rows, dict], None]] = {
    "f1_cohort_design": _rows_cohort,
    "f2_trajectories": _rows_trajectories,
    "f3_primary_tests": _rows_primary_tests,
    "f4_operating_characteristics": _rows_operating_characteristics,
    "f5_axis_diagnostics": _rows_axis_diagnostics,
    "f6_block_phase": _rows_block_phase,
    "f7_nist_bridge": _rows_nist_bridge,
    "f8_sensitivities": _rows_sensitivities,
    "f9_rank_sweep": _rows_rank_sweep,
}
assert tuple(_ROW_BUILDERS) == tuple(REPORT_FIGURES), "every figure of REPORT_FIGURES needs its rows, in its order"


def figure_rows(inputs: dict) -> dict[str, list[dict[str, str]]]:
    """The data rows of every figure of ``REPORT_FIGURES``, in order (design D4).

    Parameters
    ----------
    inputs:
        ``_load_report_inputs`` (its gates have run).

    Returns
    -------
    dict
        Figure stem → its rows (``FIGURE_CSV_COLUMNS``, every value a string),
        in drawing order.
    """
    out: dict[str, list[dict[str, str]]] = {}
    for stem, build in _ROW_BUILDERS.items():
        rows = _Rows(stem, inputs)
        try:
            build(rows, inputs)
        except Exception as e:
            raise RuntimeError(f"figure {stem}: its data rows failed ({type(e).__name__}: {e}); nothing was written") from e
        out[stem] = rows.rows
    return out


def rows_csv(rows: list[dict[str, str]]) -> bytes:
    """A figure's data CSV: the header and its rows, ``\\n`` line endings, minimal quoting, a final newline."""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(FIGURE_CSV_COLUMNS)
    for row in rows:
        writer.writerow([row[c] for c in FIGURE_CSV_COLUMNS])
    return buf.getvalue().encode("utf-8")


def read_rows_csv(data: bytes) -> list[dict[str, str]]:
    """The rows of a figure's data CSV, as ``rows_csv`` wrote them; stops on another header."""
    reader = csv.reader(io.StringIO(data.decode("utf-8"), newline=""))
    header = next(reader, None)
    if header is None or tuple(header) != FIGURE_CSV_COLUMNS:
        raise ValueError(f"the data CSV's header is {header!r}, not {list(FIGURE_CSV_COLUMNS)!r}")
    return [dict(zip(FIGURE_CSV_COLUMNS, row, strict=True)) for row in reader]


# --- the drawing -------------------------------------------------------------------


class _Values:
    """A figure's rows by key, for the drawing: every drawn value is read here."""

    def __init__(self, rows: list[dict[str, str]]) -> None:
        self.rows = rows
        self.by_key = {row["key"]: row["value"] for row in rows}

    def __call__(self, key: str) -> str:
        return self.by_key[key]

    def f(self, key: str) -> float:
        return float(self.by_key[key])

    def parts(self, index: int, *, prefix: tuple[str, ...] = (), length: int | None = None) -> list[str]:
        """The distinct ``index``-th parts of the keys that start with ``prefix`` (and have ``length`` parts), in row order."""
        out: dict[str, None] = {}
        for row in self.rows:
            parts = row["key"].split("|")
            if tuple(parts[: len(prefix)]) == prefix and (length is None or len(parts) == length) and len(parts) > index:
                out[parts[index]] = None
        return list(out)


@contextlib.contextmanager
def _bundled_fonts() -> Generator[None, None, None]:
    """Restrict matplotlib's font list to the bundled DejaVu Sans files of ``FIGURE_STYLE``, by path, while drawing."""
    ttf = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    entries = [font_manager.ttfFontProperty(font_manager.get_font(ttf / name)) for name in FIGURE_STYLE["fonts"].values()]
    manager = font_manager.fontManager
    saved = manager.ttflist
    manager.ttflist = entries
    manager._findfont_cached.cache_clear()
    try:
        yield
    finally:
        manager.ttflist = saved
        manager._findfont_cached.cache_clear()


def _header(fig: Figure, stem: str) -> None:
    """The fixed title and subtitle of ``REPORT_FIGURES`` and the footer naming the data CSV."""
    entry, height = REPORT_FIGURES[stem], fig.get_figheight()
    fig.text(0.01, 1 - 0.12 / height, entry["title"], fontsize=12, fontweight="bold", va="top")
    fig.text(0.01, 1 - 0.40 / height, entry["subtitle"], fontsize=9, color=_PAL["ink2"], va="top")
    fig.text(
        0.01, 0.08 / height,
        f"Data: {stem}.csv, one row per plotted value with its source file and field; the inputs and their sha256 are "
        "in this file's metadata.",
        fontsize=7.5, color=_PAL["muted"], va="bottom",
    )


def _margins(fig: Figure, *, top: float, bottom: float, **kwargs) -> None:
    """``subplots_adjust`` with the top and bottom margins in inches."""
    height = fig.get_figheight()
    fig.subplots_adjust(top=1 - top / height, bottom=bottom / height, **kwargs)


def _plain(ax, *, x: bool = True, y: bool = True) -> None:
    if not x:
        ax.grid(axis="x", visible=False)
    if not y:
        ax.grid(axis="y", visible=False)


def _null_box_h(ax, y: float, q50: float, q95: float, q99: float, observed: float, *, color: str, size: float = 8) -> None:
    """A horizontal null glyph: box q50 to q95, whisker to q99, the observed dot."""
    hw = 0.18
    ax.plot([q95, q99], [y, y], color=_PAL["muted"], lw=1, zorder=1)
    ax.add_patch(Rectangle((q50, y - hw), q95 - q50, 2 * hw, color=_PAL["grid"], lw=0, zorder=1))
    ax.plot([q95, q95], [y - hw, y + hw], color=_PAL["ink2"], lw=1.2, zorder=2)
    ax.plot([q50, q50], [y - hw, y + hw], color=_PAL["muted"], lw=1, zorder=2)
    ax.plot(observed, y, "o", color=color, ms=size, markeredgecolor=_PAL["surface"], markeredgewidth=1.5, zorder=4)


def _draw_cohort(fig: Figure, v: _Values) -> None:
    dxs = list(STAGE_RULE["map"].items())
    phases = ANALYSIS_COVARIATES["phase"]["levels"]
    sexes = v.parts(0, length=2)
    axes = fig.subplots(1, len(sexes), sharey=True, sharex=True)
    _margins(fig, top=1.0, bottom=0.6, left=0.15, right=0.98, wspace=0.08)
    y = np.arange(len(dxs))[::-1].astype(float)
    h = 0.36
    counts = [v.f(f"{sex}|{dx}|{p}") for sex in sexes for dx, _ in dxs for p in phases if v(f"{sex}|{dx}|{p}") != ABSENT]
    for ax, sex in zip(axes, sexes):
        for offset, phase in zip((h / 2 + 0.02, -h / 2 - 0.02), phases):
            for yy, (dx, _) in zip(y + offset, dxs):
                value = v(f"{sex}|{dx}|{phase}")
                if value == ABSENT:
                    ax.annotate("none", (0, yy), xytext=(3, 0), textcoords="offset points", va="center", fontsize=8,
                                color=_PAL["muted"])
                    continue
                ax.barh(yy, float(value), height=h, color=_PAL["run"][phase], linewidth=0)
                ax.annotate(_count(value), (float(value), yy), xytext=(3, 0), textcoords="offset points", va="center",
                            fontsize=8, color=_PAL["ink2"])
        for k in range(1, len(dxs)):
            if dxs[k][1] != dxs[k - 1][1]:
                ax.axhline((y[k] + y[k - 1]) / 2, color=_PAL["axis"], lw=0.8)
        ax.set_xlim(0, max(counts) * 1.15)
        ax.set_title(f"{sex} (n = {_count(v(f'{sex}|all'))})")
        ax.set_xlabel("participants")
        _plain(ax, y=False)
    axes[0].set_yticks(y, [f"{dx} → stage {stage}" for dx, stage in dxs])
    for ax in axes:
        ax.tick_params(axis="y", length=0)
    handles = [Line2D([], [], color=_PAL["run"][p], lw=8, label=f"p180 run {p}") for p in phases]
    fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.98, 1 - 0.55 / fig.get_figheight()), ncol=2, fontsize=8.5)


def _draw_trajectories(fig: Figure, v: _Values) -> None:
    groups = v.parts(0, length=3)
    stages = v.parts(1, prefix=(groups[0],), length=3)
    components = v.parts(2, prefix=(groups[0], stages[0]), length=3)
    ncols = 4
    nrows = math.ceil(len(components) / ncols)
    axes = np.atleast_2d(fig.subplots(nrows, ncols))
    _margins(fig, top=1.55, bottom=0.75, left=0.06, right=0.98, wspace=0.32, hspace=0.85)
    x = np.arange(len(stages))
    threshold = v("threshold")
    for ax, component in zip(axes.flat, components):
        for group in groups:
            ax.plot(x, [v.f(f"{group}|{st}|{component}") for st in stages], color=_PAL["sex"][group], lw=2, marker="o",
                    ms=6, markeredgecolor=_PAL["surface"], markeredgewidth=1.5, zorder=3)
        ax.axhline(0, color=_PAL["axis"], lw=0.8, zorder=1)
        ax.set_xticks(x, stages)
        ax.set_xlim(-0.3, len(stages) - 0.7)
        _plain(ax, x=False)
        ax.set_title(component, fontsize=10, pad=30)
        flags = []
        for variable in v.parts(2, prefix=(component, "flag"), length=4):
            text = f"{variable} {_num(v(f'{component}|flag|{variable}|spearman'), '.3f')}"
            if f"{component}|flag|{variable}|partial_spearman" in v.by_key:
                text += f" (partial {_num(v(f'{component}|flag|{variable}|partial_spearman'), '.3f')})"
            flags.append(text)
        note = f"sex-difference share {_num(v(f'{component}|share'), '.3f')}"
        if flags:
            note += f"\n|ρ| ≥ {threshold}: " + ", ".join(flags)
        ax.text(0, 1.03, note, transform=ax.transAxes, fontsize=7.5, color=_PAL["ink2"], va="bottom", linespacing=1.3)
    for ax in list(axes.flat)[len(components):]:
        ax.set_visible(False)
    for ax in axes[:, 0]:
        ax.set_ylabel("LS-mean latent score")
    handles = [Line2D([], [], color=_PAL["sex"][g], lw=2, marker="o", label=g) for g in groups]
    handles.append(Line2D([], [], ls="", label=f"CV-selected rank {_count(v('rank'))}"))
    fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.99, 1 - 0.5 / fig.get_figheight()), ncol=3)


def _draw_primary_tests(fig: Figure, v: _Values) -> None:
    statistics = v.parts(0, length=2)
    axes = fig.subplots(1, len(statistics))
    _margins(fig, top=1.15, bottom=1.25, left=0.03, right=0.98, wspace=0.12)
    for ax, s in zip(axes, statistics):
        q50, q95, q99, obs = (v.f(f"{s}|{k}") for k in ("null_q50", "null_q95", "null_q99", "observed"))
        _null_box_h(ax, 0, q50, q95, q99, obs, color=_PAL["ink"])
        ax.set_ylim(-0.6, 0.75)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        _plain(ax, y=False)
        ax.set_xlim(0, max(q99, obs) * 1.12)
        ax.set_title(_STAT_TITLE[s])
        ax.annotate(f"observed {_fmt(v.f(f'{s}|observed'))}\np {_fmt(v.f(f'{s}|p'))} (α {v('alpha')})",
                    (obs, 0.2), xytext=(obs, 0.5), ha="center", fontsize=8.5, color=_PAL["ink"],
                    arrowprops={"arrowstyle": "-", "color": _PAL["ink2"], "lw": 0.6})
        for q in ("q50", "q95", "q99"):
            ax.text(v.f(f"{s}|null_{q}"), -0.3, q, ha="center", va="top", fontsize=7, color=_PAL["muted"])
        ax.text(0, -0.32, f"highest rejection rate measured at this design {_fmt(v.f(f'{s}|max_rate'), '.3f')} "
                f"(power floor {_fmt(v.f(f'{s}|floor'))})", transform=ax.get_xaxis_transform(), fontsize=7.5,
                color=_PAL["ink2"], va="top")


def _draw_operating_characteristics(fig: Figure, v: _Values) -> None:
    statistics = v.parts(1, prefix=("power",), length=3)
    axes = fig.subplots(1, 1 + len(statistics), gridspec_kw={"width_ratios": [1.25, *([1] * len(statistics))]})
    _margins(fig, top=1.05, bottom=0.8, left=0.115, right=0.98, wspace=0.32)
    alpha, bound = v.f("size|alpha"), v.f("size|bound")
    readings = [(m, s) for m in v.parts(1, prefix=("size",), length=4) for s in v.parts(2, prefix=("size", m), length=4)]
    ax = axes[0]
    ys = np.arange(len(readings))[::-1]
    ax.axvline(alpha, color=_PAL["muted"], lw=0.8)
    ax.axvline(bound, color=_PAL["ink2"], lw=1, ls=(0, (3, 2)))
    for yy, (mode, s) in zip(ys, readings):
        ax.errorbar(v.f(f"size|{mode}|{s}|rate"), yy, xerr=1.96 * v.f(f"size|{mode}|{s}|monte_carlo_se"), fmt="o",
                    color=_PAL["ink"], ms=6, ecolor=_PAL["muted"], elinewidth=1, capsize=0)
    ax.set_yticks(ys, [f"{s} · {mode}" for mode, s in readings])
    ax.tick_params(axis="y", length=0)
    _plain(ax, y=False)
    ax.set_xlim(0, max(bound, max(v.f(f"size|{m}|{s}|rate") + 1.96 * v.f(f"size|{m}|{s}|monte_carlo_se") for m, s in readings)) * 1.25)
    ax.set_xlabel("rejection rate with no effect")
    ax.set_title("size", pad=14)
    ax.text(bound, 1.0, f" bound {_fmt(bound, '.4f')}", transform=ax.get_xaxis_transform(), fontsize=7, color=_PAL["ink2"],
            va="bottom")
    ax.text(alpha, 1.0, f"α {v('size|alpha')} ", transform=ax.get_xaxis_transform(), fontsize=7, color=_PAL["muted"],
            va="bottom", ha="right")
    for ax, s in zip(axes[1:], statistics):
        effects = [k for k in v.parts(2, prefix=("power", s), length=4) if k.startswith("e")]
        eff = [v.f(f"power|{s}|{k}|effect") for k in effects]
        rate = [v.f(f"power|{s}|{k}|rate") for k in effects]
        se = [1.96 * v.f(f"power|{s}|{k}|monte_carlo_se") for k in effects]
        floor = v.f(f"power|{s}|floor")
        ax.axhline(floor, color=_PAL["ink2"], lw=1, ls=(0, (3, 2)))
        ax.axhline(alpha, color=_PAL["muted"], lw=0.8)
        ax.errorbar(eff, rate, yerr=se, fmt="o", color=_PAL["ordinal"][1], ms=6, ecolor=_PAL["ordinal"][0], elinewidth=1,
                    capsize=0, markeredgecolor=_PAL["surface"], zorder=3)
        ax.set_ylim(0, 1)
        ax.set_xlim(0, max(eff) * 1.08)
        ax.set_xlabel(f"effect ({v(f'power|{s}|mode')} construction)")
        ax.set_title(f"power · {s}")
        ax.text(max(eff) * 1.06, floor + 0.02, f"floor {_fmt(floor)}", ha="right", fontsize=7, color=_PAL["ink2"])
        ax.annotate(f"max {_fmt(v.f(f'power|{s}|max_rate'), '.3f')}", (v.f(f"power|{s}|effect_at_max"), v.f(f"power|{s}|max_rate")),
                    xytext=(0, 9), textcoords="offset points", ha="center", fontsize=8, color=_PAL["ink"])
    axes[1].set_ylabel(f"rejection rate (α {v('size|alpha')})")


def _draw_axis_diagnostics(fig: Figure, v: _Values) -> None:
    components = v.parts(0, length=3)
    components = [c for c in components if c.startswith("pls_")]
    variables = v.parts(1, prefix=(components[0],), length=3)
    variables = [x for x in variables if not x.startswith("loading_share_")]
    blocks = [k.removeprefix("loading_share_") for k in v.parts(1, prefix=(components[0],), length=2)]
    limit = FIGURE_STYLE["correlation_limit"]
    cmap = LinearSegmentedColormap.from_list("bluegreyred", list(_PAL["diverging"]))
    norm = Normalize(-limit, limit)
    axes = fig.subplots(1, 3, gridspec_kw={"width_ratios": [8, 8, 3.2]})
    _margins(fig, top=1.0, bottom=1.0, left=0.06, right=0.98, wspace=0.12)
    for ax, (column, flag, title) in zip(axes[:2], (
        ("spearman", "flag_raw", "Spearman ρ"),
        ("partial_spearman", "flag_partial", "partial ρ (given the six design columns)"),
    )):
        for i, c in enumerate(components):
            for j, var in enumerate(variables):
                value = v(f"{c}|{var}|{column}")
                if value == "":
                    ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, color=_PAL["surface"], lw=0))
                    ax.text(j, i, "—", ha="center", va="center", color=_PAL["muted"], fontsize=8)
                    continue
                rho = float(value)
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, color=cmap(norm(rho)), lw=0))
                if v(f"{c}|{var}|{flag}") == "True":
                    ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec=_PAL["ink"], lw=1.4, zorder=3))
                    ax.text(j, i, _num(value, ".3f"), ha="center", va="center", fontsize=7.5,
                            color=_PAL["white"] if abs(rho) > 0.45 else _PAL["ink"], zorder=4)
        ax.set_xlim(-0.5, len(variables) - 0.5)
        ax.set_ylim(len(components) - 0.5, -0.5)
        ax.set_xticks(range(len(variables)), variables, rotation=35, ha="right")
        ax.set_yticks(range(len(components)), components if ax is axes[0] else [])
        ax.tick_params(length=0)
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title(title)
    mappable = ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(mappable, ax=list(axes[:2]), orientation="horizontal", fraction=0.04, pad=0.24, aspect=50)
    cbar.solids.set_rasterized(False)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(labelsize=7)
    cbar.ax.set_xlabel(f"ρ (outlined: |ρ| ≥ {v('threshold')})", fontsize=7.5)
    ax = axes[2]
    y = np.arange(len(components))
    left = np.zeros(len(components))
    for block in blocks:
        shares = np.array([v.f(f"{c}|loading_share_{block}") for c in components])
        ax.barh(y, shares, left=left, color=_PAL["block"][block], height=0.7, linewidth=0.8, edgecolor=_PAL["surface"])
        left += shares
    feature_share = v.f("feature_share|p180")
    ax.axvline(feature_share, color=_PAL["ink"], lw=1, ls=(0, (3, 2)))
    ax.set_ylim(len(components) - 0.5, -0.5)
    ax.set_yticks([])
    ax.set_xlim(0, 1.01)
    ax.grid(False)
    ax.set_title("loading share per block")
    ax.set_xlabel(f"dashed: p180 share of the joint\nfeatures {_num(v('feature_share|p180'), '.3f')}", fontsize=8)
    ax.text(0.03, 0, blocks[0], color=_PAL["ink"], fontsize=7.5, va="center")
    ax.text(0.97, 0, blocks[-1], color=_PAL["white"], fontsize=7.5, va="center", ha="right")


def _draw_block_phase(fig: Figure, v: _Values) -> None:
    exports = v.parts(0, length=3)
    blocks = v.parts(1, prefix=(exports[0],), length=3)
    threshold = v.f("threshold")
    rules = ["READING_RULES", *(EXPORT_VARIANT_RULE_SETS[e]["rules"] for e in exports[1:-1]), "STAGE_SENSITIVITY_READING_RULES"]
    ys, group_y, separators = [], [], []
    y = 0.0
    for k, e in enumerate(exports):
        if k == 0 or rules[k] != rules[k - 1]:
            if k:
                separators.append(y + 0.3)
                y -= 0.4
            group_y.append((rules[k], y))
            y -= 0.8
        ys.append(y)
        y -= 1
    axes = fig.subplots(1, len(blocks), sharey=True)
    _margins(fig, top=1.05, bottom=0.8, left=0.24, right=0.98, wspace=0.08)
    for ax, block in zip(axes, blocks):
        ax.axvline(threshold, color=_PAL["ink2"], lw=1, ls=(0, (3, 2)))
        for yy, e in zip(ys, exports):
            pcs = v.parts(2, prefix=(e, block), length=3)
            for k, pc in enumerate(pcs):
                ax.plot(abs(v.f(f"{e}|{block}|{pc}")), yy + (1 - k) * 0.2, "o", color=_PAL["ordinal"][k % 3], ms=6.5,
                        markeredgecolor=_PAL["surface"], markeredgewidth=1.2)
        for sep in separators:
            ax.axhline(sep, color=_PAL["axis"], lw=0.6)
        ax.set_xlim(-0.02, 1)
        ax.set_title(f"{block} block")
        ax.set_xlabel("|Spearman ρ| of the block PC with phase")
        _plain(ax, y=False)
        ax.text(threshold, 1.0, f" {v('threshold')}", transform=ax.get_xaxis_transform(), fontsize=7, color=_PAL["ink2"],
                va="bottom")
    axes[0].set_yticks(ys, exports)
    for ax in axes:
        ax.tick_params(axis="y", length=0)
    for name, gy in group_y:
        axes[0].text(-0.02, gy, name, transform=axes[0].get_yaxis_transform(), ha="right", fontsize=7.5, fontweight="bold",
                     color=_PAL["ink"], va="center")
    pcs = v.parts(2, prefix=(exports[0], blocks[0]), length=3)
    handles = [Line2D([], [], ls="", marker="o", color=_PAL["ordinal"][k % 3], label=pc) for k, pc in enumerate(pcs)]
    fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.98, 1 - 0.5 / fig.get_figheight()), ncol=len(pcs))


def _draw_nist_bridge(fig: Figure, v: _Values) -> None:
    metabolites = [m for m in v.parts(0, length=2) if m != "legend"]
    ax = fig.subplots()
    _margins(fig, top=1.0, bottom=0.65, left=0.07, right=0.98)
    marker = {"FIA": "o", "UPLC": "s"}
    labelled = 0
    for i, m in enumerate(metabolites):
        b = v.f(f"{m}|b")
        se = 1.96 * float(v(f"{m}|se_b")) if v(f"{m}|se_b") != "" else 0.0
        bridged = v(f"{m}|bridged") == "True"
        if se:
            ax.plot([i, i], [b - se, b + se], color=_PAL["grid"] if bridged else _PAL["axis"], lw=1, zorder=1)
        ax.plot(i, b, marker[v(f"{m}|kit")], ms=4.5, zorder=3, color=_PAL["ink"] if bridged else _PAL["surface"],
                markeredgecolor=_PAL["ink"] if bridged else _PAL["muted"], markeredgewidth=1)
        if not bridged:
            label_y = max((0.45, 0.62, 0.79)[labelled % 3], b + se + 0.1)
            labelled += 1
            ax.annotate(v(f"{m}|nist_column"), (i, b + se), xytext=(i, label_y), ha="center", fontsize=7.5,
                        color=_PAL["ink2"], va="bottom", arrowprops={"arrowstyle": "-", "color": _PAL["axis"], "lw": 0.6})
    ax.axhline(0, color=_PAL["axis"], lw=0.8)
    ax.set_xticks([])
    _plain(ax, x=False)
    ax.set_xlim(-1.5, len(metabolites) + 0.5)
    ax.set_xlabel(f"{_count(v('legend|metabolites'))} p180 metabolites, ordered by b")
    ax.set_ylabel("b = log2 ADNI-1 − log2 ADNI-GO/2")
    handles = [
        Line2D([], [], ls="", marker="o", color=_PAL["ink"], label=f"FIA, bridged ({_count(v('legend|FIA'))})"),
        Line2D([], [], ls="", marker="s", color=_PAL["ink"], label=f"UPLC, bridged ({_count(v('legend|UPLC'))})"),
        Line2D([], [], ls="", marker="o", color=_PAL["surface"], markeredgecolor=_PAL["muted"],
               label=f"not bridged ({_count(v('legend|not_bridged'))})"),
    ]
    ax.legend(handles=handles, loc="upper left", ncol=3)


def _draw_sensitivities(fig: Figure, v: _Values) -> None:
    names = v.parts(0, length=2)
    statistics = v.parts(1, prefix=("primary",), length=3)
    labels, ys, group_y, separators = [], [], [], []
    y = 0.0
    previous = None
    for name in names:
        rules = _rule_set_of(name)
        if rules != previous:
            if previous is not None:
                separators.append(y + 0.3)
                y -= 0.4
            group_y.append((rules, y))
            y -= 0.8
            previous = rules
        labels.append(f"{name} (rank {_count(v(f'{name}|selected_rank'))})")
        ys.append(y)
        y -= 1
    axes = fig.subplots(1, len(statistics), sharey=True)
    _margins(fig, top=1.3, bottom=0.8, left=0.2, right=0.98, wspace=0.08)
    alpha = v.f("alpha")
    p_all = [v.f(f"{n}|{s}|p") for n in names for s in statistics] + [v.f(f"primary|{s}|p") for s in statistics]
    low = 10 ** math.floor(math.log10(min(p_all) / 1.5))
    ticks = [t for t in (0.0001, 0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0) if t >= low]
    for ax, s in zip(axes, statistics):
        p0 = v.f(f"primary|{s}|p")
        ax.axvline(alpha, color=_PAL["ink2"], lw=1, ls=(0, (3, 2)))
        ax.axvline(p0, color=_PAL["ink"], lw=1.4)
        ax.text(p0, 1.0, f"primary p {_num(v(f'primary|{s}|p'))}", transform=ax.get_xaxis_transform(), fontsize=7.5,
                color=_PAL["ink"], ha="center", va="bottom")
        ax.text(alpha, 1.0, f"α {v('alpha')} ", transform=ax.get_xaxis_transform(), fontsize=7.5, color=_PAL["ink2"],
                ha="right", va="bottom")
        for yy, name in zip(ys, names):
            p = v.f(f"{name}|{s}|p")
            rejected = v(f"{name}|{s}|rejected") == "True"
            ax.plot(p, yy, "o", ms=7, zorder=3, color=_PAL["ink"] if rejected else _PAL["surface"],
                    markeredgecolor=_PAL["ink"], markeredgewidth=1.2)
            status = v(f"{name}|{s}|status")
            if status != "same":
                ax.annotate(status, (p, yy), xytext=(7, 0), textcoords="offset points", fontsize=7, color=_PAL["ink2"],
                            va="center", bbox={"boxstyle": "square,pad=0.15", "fc": _PAL["surface"], "ec": "none"}, zorder=5)
        for sep in separators:
            ax.axhline(sep, color=_PAL["axis"], lw=0.6)
        ax.set_xscale("log")
        ax.set_xlim(low, 1.05)
        ax.set_xticks(ticks, [format(t, "g") for t in ticks])
        ax.minorticks_off()
        _plain(ax, y=False)
        ax.set_title(_STAT_TITLE[s], pad=16)
        ax.set_xlabel("RRPP p-value (log scale)")
    axes[0].set_yticks(ys, labels)
    for ax in axes:
        ax.tick_params(axis="y", length=0)
    for name, gy in group_y:
        axes[0].text(-0.02, gy, name, transform=axes[0].get_yaxis_transform(), ha="right", fontsize=7.5, fontweight="bold",
                     color=_PAL["ink"], va="center")
    handles = [Line2D([], [], ls="", marker="o", color=_PAL["ink"], label="rejected (ANALYSIS_REJECTION_RULE)"),
               Line2D([], [], ls="", marker="o", color=_PAL["surface"], markeredgecolor=_PAL["ink"], label="not rejected")]
    fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.98, 1 - 0.55 / fig.get_figheight()), ncol=2)


def _draw_rank_sweep(fig: Figure, v: _Values) -> None:
    runs = v.parts(0, length=2)
    statistics = v.parts(1, prefix=(runs[0],), length=3)
    ranks = {run: v.f(f"{run}|rank") for run in runs}
    axes = fig.subplots(1, len(statistics))
    _margins(fig, top=1.25, bottom=0.8, left=0.06, right=0.98, wspace=0.22)
    for ax, s in zip(axes, statistics):
        top = 0.0
        for run in runs:
            k = ranks[run]
            q50, q95, q99, obs = (v.f(f"{run}|{s}|{q}") for q in ("null_q50", "null_q95", "null_q99", "observed"))
            primary = run == "primary"
            ax.add_patch(Rectangle((k - 0.32, q50), 0.64, q95 - q50, color=_PAL["grid"], lw=0, zorder=1))
            ax.plot([k, k], [q95, q99], color=_PAL["muted"], lw=1, zorder=1)
            ax.plot([k - 0.32, k + 0.32], [q95, q95], color=_PAL["ink2"], lw=1.2, zorder=2)
            ax.plot(k, obs, "o", ms=8 if primary else 6.5, zorder=4, color=_PAL["ink"] if primary else _PAL["ordinal"][1],
                    markeredgecolor=_PAL["surface"], markeredgewidth=1.3)
            top = max(top, q99, obs)
        ax.set_xticks([ranks[r] for r in runs], [_count(v(f"{r}|rank")) for r in runs])
        ax.set_xlim(min(ranks.values()) - 1, max(ranks.values()) + 1)
        ax.set_ylim(0, top * 1.08)
        _plain(ax, x=False)
        ax.set_xlabel("PLS-DA rank")
        ax.set_title(_STAT_TITLE[s])
    handles = [
        Line2D([], [], ls="", marker="o", color=_PAL["ink"], label=f"primary (CV-selected rank {_count(v('primary|rank'))})"),
        Line2D([], [], ls="", marker="o", color=_PAL["ordinal"][1], label="forced rank (RANK_SENSITIVITY_LADDER)"),
        Rectangle((0, 0), 1, 1, color=_PAL["grid"], label="that rank's null, q50 to q95 (whisker to q99)"),
    ]
    fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.98, 1 - 0.55 / fig.get_figheight()), ncol=3)


#: Per figure its drawing and its size in inches (design D6; the drafts' sizes, ``f6`` taller for its eight exports).
_DRAWINGS: dict[str, tuple[Callable[[Figure, _Values], None], tuple[float, float]]] = {
    "f1_cohort_design": (_draw_cohort, (10, 4.4)),
    "f2_trajectories": (_draw_trajectories, (12, 7.2)),
    "f3_primary_tests": (_draw_primary_tests, (12, 4.0)),
    "f4_operating_characteristics": (_draw_operating_characteristics, (12.5, 3.9)),
    "f5_axis_diagnostics": (_draw_axis_diagnostics, (12.5, 4.8)),
    "f6_block_phase": (_draw_block_phase, (11, 5.0)),
    "f7_nist_bridge": (_draw_nist_bridge, (12, 4.4)),
    "f8_sensitivities": (_draw_sensitivities, (12.5, 8.2)),
    "f9_rank_sweep": (_draw_rank_sweep, (12.5, 4.5)),
}
assert tuple(_DRAWINGS) == tuple(REPORT_FIGURES), "every figure of REPORT_FIGURES needs its drawing, in its order"


def _svg_metadata(stem: str, inputs: dict) -> dict[str, str | None]:
    """The SVG's metadata: the title, each input with its sha256, the drawing library; no date (design D6)."""
    files = inputs["files"]
    return {
        "Title": REPORT_FIGURES[stem]["title"],
        "Description": "\n".join(
            f"{files[role][name]['path']} sha256 {files[role][name]['sha256']}" for role, name in REPORT_FIGURES[stem]["inputs"]
        ),
        "Creator": f"adni-sexdiff report, matplotlib {matplotlib.__version__}",
        "Date": None,
    }


def draw_figure(stem: str, rows: list[dict[str, str]], inputs: dict) -> bytes:
    """One figure's SVG bytes, drawn from its rows in memory (design D6); nothing touches the disk."""
    draw, size = _DRAWINGS[stem]
    with matplotlib.rc_context():
        matplotlib.rcdefaults()
        matplotlib.rcParams.update(FIGURE_STYLE["rc"])
        with _bundled_fonts():
            fig = Figure(figsize=size)
            FigureCanvasSVG(fig)
            draw(fig, _Values(rows))
            _header(fig, stem)
            buf = io.BytesIO()
            fig.savefig(buf, format="svg", metadata=_svg_metadata(stem, inputs))
    return buf.getvalue()


def draw_figures(inputs: dict, rows: dict[str, list[dict[str, str]]]) -> dict[str, bytes]:
    """Every figure's SVG bytes, in ``REPORT_FIGURES`` order; a figure that fails stops the step naming it.

    Parameters
    ----------
    inputs:
        ``_load_report_inputs`` (for the input hashes of the metadata).
    rows:
        ``figure_rows(inputs)``: every drawn value is read from them.

    Returns
    -------
    dict
        Figure stem → SVG bytes.
    """
    if matplotlib.__version__ != MATPLOTLIB_VERSION:
        raise RuntimeError(
            f"matplotlib {matplotlib.__version__} is loaded but the pin is {MATPLOTLIB_VERSION} (MATPLOTLIB_VERSION); run "
            "`uv sync --locked`; nothing was written"
        )
    out: dict[str, bytes] = {}
    for stem in REPORT_FIGURES:
        try:
            out[stem] = draw_figure(stem, rows[stem], inputs)
        except Exception as e:
            raise RuntimeError(f"figure {stem}: drawing failed ({type(e).__name__}: {e}); nothing was written") from e
    return out
