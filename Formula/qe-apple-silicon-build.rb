class QeAppleSiliconBuild < Formula
  desc "One-command installer/updater and migration validator for QE on Apple Silicon"
  homepage "https://github.com/shahpoll/qe_apple_silicon_build"
  license "MIT"

  # Local development formula; stable release formula is published in shahpoll/homebrew-qe.
  head "https://github.com/shahpoll/qe_apple_silicon_build.git", branch: "main"

  depends_on "python@3.13"
  depends_on "open-mpi"
  depends_on "gcc"
  depends_on "cmake"
  depends_on "veclibfort"

  def install
    libexec.install Dir["*"]
    bin.install_symlink libexec/"bin/qe-apple-silicon-build"
  end

  test do
    assert_match "Usage:", shell_output("#{bin}/qe-apple-silicon-build help")
  end
end
