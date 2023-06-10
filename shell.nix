{ pkgs, ... }:

pkgs.mkShell {
  buildInputs = with pkgs.python3Packages; [
    fastapi
    uvicorn
    sqlalchemy
    sqlalchemy.optional-dependencies.aiosqlite
    python-jose
    passlib
    argon2-cffi
  ];
}
