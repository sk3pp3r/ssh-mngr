class SshMngr < Formula
  include Language::Python::Virtualenv

  desc "Beautiful terminal SSH connection manager — like mRemoteNG for your terminal"
  homepage "https://github.com/sk3pp3r/ssh-mngr"
  url "https://files.pythonhosted.org/packages/a7/19/fb11b736a8d17dda14795a1446233d43c6c3c2ad81f2adf130177cdbf658/ssh_mngr-0.1.4.tar.gz"
  sha256 "2c936e41e68067be973d8ca2d5eea37e49e36a54350b88b547ba012910fe7d90"
  license "MIT"

  depends_on "python@3.13"

  def install
    venv = virtualenv_create(libexec, "python3.13")
    system libexec/"bin/python3", "-m", "ensurepip"
    system libexec/"bin/python3", "-m", "pip", "install",
           "--prefer-binary", "--no-cache-dir", "ssh-mngr==0.1.4"

    (bin/"ssh-mngr").write_env_script(libexec/"bin/ssh-mngr",
      PATH: "#{libexec}/bin:${PATH}")
    (bin/"ssm").write_env_script(libexec/"bin/ssm",
      PATH: "#{libexec}/bin:${PATH}")
  end

  test do
    assert_match version.to_s,
      shell_output("#{libexec}/bin/python3 -c 'import ssh_mngr; print(ssh_mngr.__version__)'")
  end
end
