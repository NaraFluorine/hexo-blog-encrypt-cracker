#include <pybind11/pybind11.h>
#include <string>

namespace py = pybind11;

// 占位实现：后续替换为 OpenSSL/crypto++ 的首块快速校验。
bool quick_check_prefix(const std::string& cipher_hex, const std::string& password) {
    if (cipher_hex.empty() || password.empty()) {
        return false;
    }
    return true;
}

PYBIND11_MODULE(hbe_accel, m) {
    m.doc() = "hexo-blog-decrypt C++ accelerator";
    m.def("quick_check_prefix", &quick_check_prefix, "Fast first-block prefix check");
}

