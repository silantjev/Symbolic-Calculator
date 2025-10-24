import os
from conan import ConanFile
from conan.tools.files import copy, symlinks
# from conan.tools.cmake import CMakeToolchain, CMakeDeps

class CppCilentConan(ConanFile):
    name = "cpp_client"
    version = "3.0.0"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"
    requires = "qt/5.15.7"

    def configure(self):
        self.options["qt"].shared = True
        # self.options["qt"].qtmultimedia = False
        # self.options["qt"].qtwebengine = False
        # self.options["qt"].with_mysql = False
        self.options["qt"].with_icu = False
        self.options["qt"].with_harfbuzz = False
        self.options["qt"].with_pcre2 = False
        self.options["qt"].openssl = False
        self.options["qt"].with_zlib = True
        self.options["qt"].with_libjpeg = False
        self.options["qt"].with_libpng = False
        self.options["qt"].with_sqlite3 = False
        self.options["qt"].qtbase = True
        self.options["qt"].qtwidgets = True
        self.options["qt"].qtgui = True
        self.options["qt"].qtnetwork = True
        self.settings.compiler.cppstd=17

    def generate(self):
        bin_dir = os.path.join(self.build_folder, "..", "bin")
        lib_dir = os.path.join(bin_dir, "lib")
        platforms_dir = os.path.join(bin_dir, "platforms")
        os.makedirs(lib_dir, exist_ok=True)
        os.makedirs(platforms_dir, exist_ok=True)
        
        # Копируем все shared библиотеки из зависимостей
        for dep in self.dependencies.values():
            for libdir in dep.cpp_info.libdirs:
                copy(self, "*.so*", libdir, lib_dir)
            if dep.ref.name == "qt":
                plugin_path = os.path.join(dep.package_folder, "bin", "archdatadir", "plugins", "platforms")
                if os.path.exists(plugin_path):
                    copy(self, "libqxcb.so*", plugin_path, platforms_dir)
        
        # Преобразуем симлинки и устанавливаем RPATH
        symlinks.absolute_to_relative_symlinks(self, lib_dir)
        
        # Устанавливаем RPATH для всех .so файлов
        for root, _, filenames in os.walk(bin_dir):
            for filename in filenames:
                if filename.endswith(".so") or ".so." in filename:
                    file_path = os.path.join(root, filename)
                    self.run(f"patchelf --set-rpath '$ORIGIN/../lib' {file_path}")

        # Создаем qt.conf
        qt_conf = os.path.join(bin_dir, "qt.conf")
        with open(qt_conf, 'w') as f:
            f.write("[Paths]\nPlugins=platforms\n") # Устанавливаем путь к плагинам относительно бинарника

