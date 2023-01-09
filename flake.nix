{
  description = "Weight tracker";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    {
      # Nixpkgs overlay providing the application
      overlay = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          # The application
          weight-tracker = prev.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
          };
        })
      ];
    } // (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
      in
      {
        apps = {
          weight-tracker = pkgs.weight-tracker;
        };

        defaultApp = pkgs.weight-tracker;

        devShell =
          let
            pythonPackages = pkgs.python310Packages;
          in
          pkgs.mkShell {
            buildInputs = with pythonPackages; [ python poetry debugpy venvShellHook ];
            venvDir = "./.venv";
            postVenvCreation = ''
              unset SOURCE_DATE_EPOCH
              poetry env use .venv/bin/python
              poetry install
            '';
            postShellHook = ''
              unset SOURCE_DATE_EPOCH
            '';
          };
      }));
}
