class SshMngr < Formula
  include Language::Python::Virtualenv

  desc "Beautiful terminal SSH connection manager — like mRemoteNG for your terminal"
  homepage "https://github.com/sk3pp3r/ssh-mngr"
  url "https://files.pythonhosted.org/packages/88/bc/1766f0b7c8ba5104483104ca5572fa0abe54fb03729de8a59befccc020d6/ssh_mngr-0.2.0.tar.gz"
  sha256 "6de99a0df2d56028e83a1f5babdd6a6e016099862cc8ab1b409d743f7e096ea9"
  license "MIT"

  depends_on "python@3.13"

  def install
    venv = virtualenv_create(libexec, "python3.13")
    system libexec/"bin/python3", "-m", "ensurepip"
    system libexec/"bin/python3", "-m", "pip", "install",
           "--prefer-binary", "--no-cache-dir", "ssh-mngr==0.2.0"

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
