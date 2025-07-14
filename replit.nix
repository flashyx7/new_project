
{ pkgs }: {
  deps = [
    pkgs.python312Full
    pkgs.python312Packages.pip
    pkgs.python312Packages.fastapi
    pkgs.python312Packages.uvicorn
    pkgs.python312Packages.jinja2
    pkgs.python312Packages.python-multipart
    pkgs.python312Packages.starlette
    pkgs.python312Packages.aiofiles
    pkgs.python312Packages.structlog
    pkgs.python312Packages.bcrypt
    pkgs.python312Packages.passlib
    pkgs.python312Packages.itsdangerous
    pkgs.python312Packages.sqlalchemy
    pkgs.python312Packages.pyjwt
    pkgs.python312Packages.httpx
    pkgs.python312Packages.requests
    pkgs.python312Packages.pytest
    pkgs.python312Packages.python-dotenv
    pkgs.python312Packages.python-dateutil
    pkgs.python312Packages.email-validator
    pkgs.python312Packages.python-jose
  ];
}
