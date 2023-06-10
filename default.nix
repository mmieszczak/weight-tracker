{ python3Packages, ... }:

with python3Packages;
buildPythonApplication {
  pname = "weight-tracker";
  version = "0.1.0";

  propagatedBuildInputs = [ flask ];

  src = ./.;
}
