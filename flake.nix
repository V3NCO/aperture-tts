{
  description = "Dev shell with Python 3.11 for aperture-TTS";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  inputs.unstable.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    {
      self,
      nixpkgs,
      unstable,
    }:
    let
      systems = [
        "aarch64-darwin"
        "x86_64-darwin"
        "x86_64-linux"
        "aarch64-linux"
      ];
    in
    {
      devShells = nixpkgs.lib.genAttrs systems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
          unstablePkgs = import unstable { inherit system; };
        in
        {
          default = pkgs.mkShell {
            buildInputs = [
              pkgs.cmake
              pkgs.pkg-config
              pkgs.python311
              unstablePkgs.uv
              pkgs.zlib
            ];
            shellHook = ''
              export LD_LIBRARY_PATH="${pkgs.zlib.out}/lib:$LD_LIBRARY_PATH"
              export UV_PYTHON="${pkgs.python311}/bin/python3.11"
            '';
          };
        }
      );
    };
}
