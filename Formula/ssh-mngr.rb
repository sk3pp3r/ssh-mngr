class SshMngr < Formula
  include Language::Python::Virtualenv

  desc "Beautiful terminal SSH connection manager — like mRemoteNG for your terminal"
  homepage "https://github.com/sk3pp3r/ssh-mngr"
  url "https://files.pythonhosted.org/packages/6d/1f/ac71b4b9252e826f848ed2965c14e9ab99824280dc03eca5729b7ca6ed32/ssh_mngr-0.1.1.tar.gz"
  sha256 "c53ffaf8f98e1e5f23b05b13267a6b5410b663c1b47b5eeca20b9adf5d69a987"
  license "MIT"

  depends_on "python@3.13"

  def install
    venv = virtualenv_create(libexec, "python3.13")
    system libexec/"bin/python3", "-m", "ensurepip"
    system libexec/"bin/python3", "-m", "pip", "install",
           "--prefer-binary", "--no-cache-dir", "ssh-mngr==0.1.1"

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
