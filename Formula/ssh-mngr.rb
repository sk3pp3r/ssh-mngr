class SshMngr < Formula
  include Language::Python::Virtualenv

  desc "Beautiful terminal SSH connection manager — like mRemoteNG for your terminal"
  homepage "https://github.com/sk3pp3r/ssh-mngr"
  url "https://files.pythonhosted.org/packages/61/55/757b33d4e049e6ca3cb3b1b31d6cea3428bac43b5ad8fa7602bb10d65335/ssh_mngr-0.1.2.tar.gz"
  sha256 "c704b352aa8c23d5c54ee384751d7c14836008aa2b93e9da28121a38ba36a2bc"
  license "MIT"

  depends_on "python@3.13"

  def install
    venv = virtualenv_create(libexec, "python3.13")
    system libexec/"bin/python3", "-m", "ensurepip"
    system libexec/"bin/python3", "-m", "pip", "install",
           "--prefer-binary", "--no-cache-dir", "ssh-mngr==0.1.2"

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
