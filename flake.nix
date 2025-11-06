{
  description = "Dev shell with CMake < 3.30 for building style-bert-vits2 deps";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";

  outputs = { self, nixpkgs }:
    let
      systems = [ "aarch64-darwin" "x86_64-darwin" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system:
        f (import nixpkgs { inherit system; }));
    in {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          buildInputs = [
            pkgs.cmake        # 3.29.x on 24.05
            pkgs.pkg-config
            # Optional: pin a Python that’s widely supported by ML stacks
            pkgs.python311
          ];
        };
      });
    };
}
