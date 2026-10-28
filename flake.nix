{
  description = "adni-sexdiff project development environment flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";
  };

  outputs =
    {
      self,
      nixpkgs,
      systems,
    }:
    let
      forEachSystem = nixpkgs.lib.genAttrs (import systems);
    in
    {
      devShells = forEachSystem (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              python312
              uv
            ];

            LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
              pkgs.stdenv.cc.cc.lib
              pkgs.zlib
            ];

            shellHook = ''
              export UV_PYTHON="${pkgs.python312}/bin/python"
              export UV_PYTHON_DOWNLOADS=never

              # The pinned numeric environment (constants.NUMERIC_SETTINGS,
              # change adni-portable-numerics), so that commands run in the
              # shell outside the package (motco analyze for a manifest's
              # cli_equivalent, scratch scripts) compute the same bits on
              # every machine. The package sets the same values on import.
              export NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL"
              export OPENBLAS_CORETYPE=Haswell
              export OPENBLAS_NUM_THREADS=1
              export OMP_NUM_THREADS=1

              uv sync --locked
            '';
          };
        }
      );
    };
}
