class AlldebridDl < Formula
  desc "Download files from Alldebrid magnets with directory structure preserved"
  homepage "https://github.com/jeromegsq/alldebrid-dl"
  url "https://github.com/jeromegsq/alldebrid-dl/archive/refs/tags/v1.0.0.tar.gz"
  sha256 ""
  license "MIT"

  depends_on "jq"
  depends_on "wget"
  depends_on "python3" => :recommended

  def install
    bin.install "alldebrid-dl"
  end

  test do
    assert_match "Usage", shell_output("#{bin}/alldebrid-dl 2>&1", 1)
  end
end
