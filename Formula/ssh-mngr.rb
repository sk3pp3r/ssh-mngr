class SshMngr < Formula
  include Language::Python::Virtualenv

  desc "Beautiful terminal SSH connection manager — like mRemoteNG for your terminal"
  homepage "https://github.com/sk3pp3r/ssh-mngr"
  url "https://files.pythonhosted.org/packages/8e/13/e4102f39d5f9660ddb37cd5aac8b2368ae357252aeb26cb54594f7a2f05c/ssh_mngr-0.1.5.tar.gz"
  sha256 "f233fd8f8af3c89d4855c1b73521081fecd9157dde37cdd314f0d71a42743cc9"
  license "MIT"

  depends_on "python@3.13"

  def install
    venv = virtualenv_create(libexec, "python3.13")
    system libexec/"bin/python3", "-m", "ensurepip"
    system libexec/"bin/python3", "-m", "pip", "install",
           "--prefer-binary", "--no-cache-dir", "ssh-mngr==0.1.5"

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
