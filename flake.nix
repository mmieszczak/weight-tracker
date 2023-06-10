{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
  };

  outputs = { nixpkgs, ... }:
    let
      forAllSystems = nixpkgs.lib.genAttrs [ "aarch64-linux" "x86_64-linux" ];
    in
    {
      packages = forAllSystems (system: {
        default = nixpkgs.legacyPackages.${system}.callPackage ./default.nix { inherit system; };
      });
      devShells = forAllSystems (system: {
        default = nixpkgs.legacyPackages.${system}.callPackage ./shell.nix { };
      });
    };
}
