{
  inputs = {
    hspkgs.url =
      "github:podenv/hspkgs/90eadd304c6375f926a0970f87b470e765e7f176";
  };
  outputs = { self, hspkgs }:
    let
      pkgs = hspkgs.pkgs;
      haskellExtend = hpFinal: hpPrev: {
        slacker = pkgs.haskell.lib.doJailbreak (hpPrev.callCabal2nix "slacker"
          (pkgs.fetchFromGitHub {
            owner = "velveteer";
            repo = "slacker";
            rev = "bf8e13bbc566f92f900d2cc92ebd8a6f1e46334f";
            sha256 = "sha256-X/8l6jvudzi46dWyrvOAPxdT4f2nSAISGEzqVNyelKY=";
          }) { });
      };

      hsPkgs = pkgs.hspkgs.extend haskellExtend;
      ghc = hsPkgs.ghcWithPackages (p: [ p.slacker p.lens-aeson ]);

    in {
      devShell."x86_64-linux" =
        pkgs.mkShell { buildInputs = [ ghc pkgs.ghcid ]; };
      devShells."x86_64-linux".prev = hsPkgs.shellFor {
        packages = p: [ p.slack-api ];
        buildInputs = with pkgs; [ cabal-install ghcid ];
      };
    };
}
