{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [ pkgs.apptainer pkgs.git pkgs.python3 pkgs.poppler-utils ];

          shellHook = ''
            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib pkgs.zlib pkgs.bzip2 pkgs.xz ]}:$LD_LIBRARY_PATH"
            [ -d .venv ] || python3 -m venv .venv
            source .venv/bin/activate
            pip install --quiet -r requirements.txt
          '';
        };
      });
}
