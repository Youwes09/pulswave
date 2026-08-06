{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        vtkNoGdal = pkgs.vtk.overrideAttrs (old: {
          cmakeFlags = (old.cmakeFlags or []) ++ [
            "-DVTK_MODULE_ENABLE_VTK_IOGDAL=NO"
          ];
        });
        pyEnv = pkgs.python3.withPackages (ps: with ps; [
          numpy
          scipy
          matplotlib
          pandas
          h5py
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pkgs.podman
            pkgs.apptainer
            pkgs.git
            pkgs.cmake
            vtkNoGdal
            pyEnv
            pkgs.stdenv.cc.cc.lib  # libstdc++.so.6
            pkgs.zlib              # libz.so.1
            pkgs.bzip2             # libbz2, sometimes pulled in by hdf5/numpy stack
            pkgs.xz                # liblzma, same reason
          ];

          shellHook = ''
            export PULSWAVE_ROOT=$(pwd)
            export PULSWAVE_MECHANISMS=$PULSWAVE_ROOT/mechanisms

            # manylinux wheels (e.g. cantera below) expect a normal FHS
            # /usr/lib with libstdc++, libz, etc. on it. NixOS has no such
            # path, so point the dynamic linker at nixpkgs' copies instead.
            # This list covers the common transitive deps of scientific
            # manylinux wheels; extend it if `import cantera` still fails
            # on a missing .so (the error names the library each time).
            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
              pkgs.stdenv.cc.cc.lib
              pkgs.zlib
              pkgs.bzip2
              pkgs.xz
            ]}:$LD_LIBRARY_PATH"

            # Cantera has no nixpkgs Python binding (build-system mismatch
            # between Cantera's SCons+Cython build and nixpkgs Python
            # packaging conventions). Install it from PyPI instead, into a
            # local venv layered on top of the nix-provided interpreter.
            # Pinned to 3.2.0 -- see mechanisms/README.md before bumping.
            VENV_DIR="$PULSWAVE_ROOT/.venv"
            if [ ! -d "$VENV_DIR" ]; then
              python3 -m venv "$VENV_DIR" --system-site-packages
            fi
            source "$VENV_DIR/bin/activate"
            pip install --quiet cantera==3.2.0
          '';
        };
      });
}
