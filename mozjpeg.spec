%define major 8
%define majorturbo 0
%define libname %mklibname jpeg %{major}
%define devname %mklibname -d jpeg
%define static %mklibname -s -d jpeg
%define turbo %mklibname turbojpeg %{majorturbo}
%define beta 20181202

%define major62 62
%define libname62 %mklibname jpeg %{major62}

%bcond_without java

Summary:	A MMX/SSE2 accelerated library for manipulating JPEG image files
Name:		mozjpeg
Epoch:		1
Version:	3.3.2
%if "%{beta}" != ""
Release:	0.%{beta}.1
Source0:	https://github.com/mozilla/mozjpeg/archive/v%{version}-%{beta}.tar.gz
%else
Release:	2
Source0:	https://github.com/mozilla/mozjpeg/archive/%{name}-%{version}.tar.gz
%endif
License:	wxWidgets Library License
Group:		System/Libraries
Url:		https://github.com/mozilla/mozjpeg
# These two allow automatic lossless rotation of JPEG images from a digital
# camera which have orientation markings in the EXIF data. After rotation
# the orientation markings are reset to avoid duplicate rotation when
# applying these programs again.
Source2:	http://jpegclub.org/jpegexiforient.c
Source3:	http://jpegclub.org/exifautotran.txt
Patch0:		jpeg-6b-c++fixes.patch
Patch1:		merge-libjpeg-turbo-2.0.1.patch
Patch2:		mozjpeg-libm-linkage.patch
BuildRequires:	pkgconfig(libpng)
BuildRequires:	cmake ninja
%if %{with java}
BuildRequires:	java-devel
%endif
%ifarch %{ix86} %{x86_64}
BuildRequires:	nasm
%endif

%description
This package contains a library of functions for manipulating JPEG images.
It is a high-speed, libjpeg-compatible version for x86 and x86-64
processors which uses SIMD instructions (MMX, SSE2, etc.) to accelerate
baseline JPEG compression and decompression. It is generally 2-4x as fast
as the unmodified version of libjpeg, all else being equal.

%package -n %{libname}
Summary:	A library for manipulating JPEG image format files
Group:		System/Libraries

%description -n %{libname}
This package contains the library needed to run programs dynamically
linked with libjpeg.

%package -n %{libname62}
Summary:	A library for manipulating JPEG image format files
Group:		System/Libraries

%description -n %{libname62}
This package contains the library needed to run programs dynamically
linked with libjpeg.

%package -n %{turbo}
Summary:	TurboJPEG library
Group:		System/Libraries

%description -n %{turbo}
This package contains the library needed to run programs dynamically
linked with libturbojpeg.

%package -n %{devname}
Summary:	Development tools for programs which will use the libjpeg library
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Requires:	%{turbo} = %{EVRD}
Provides:	jpeg-devel = %{EVRD}
Conflicts:	jpeg6-devel
Conflicts:	%{_lib}turbojpeg < 1:1.3.0
Obsoletes:	%{_lib}turbojpeg < 1:1.3.0
Obsoletes:	%{mklibname jpeg 62 -d} < 6b-45

%description -n	%{devname}
The libjpeg-turbo devel package includes the header files necessary for 
developing programs which will manipulate JPEG files using the
libjpeg library.

%package -n %{static}
Summary:	Static libraries for programs which will use the libjpeg library
Group:		Development/C
Requires:	%{devname} = %{EVRD}
Provides:	jpeg-static-devel = %{EVRD}
Conflicts:	jpeg6-static-devel
Obsoletes:	%{mklibname jpeg 62 -d -s} < 6b-45
Obsoletes:	%{mklibname jpeg 7 -d -s} < 7-3

%description -n %{static}
The libjpeg static devel package includes the static libraries
necessary for developing programs which will manipulate JPEG files using
the libjpeg library.

%package -n jpeg-progs
Summary:	Programs for manipulating JPEG format image files
Group:		Graphics
%rename		libjpeg-progs
%rename		jpeg6-progs

%description -n	jpeg-progs
This package contains simple client programs for accessing the
libjpeg functions.  The library client programs include cjpeg, djpeg,
jpegtran, rdjpgcom, wrjpgcom and jpegexiforient, coupled with the script
exifautotran. Cjpeg compresses an image file into JPEG format. Djpeg
decompresses a JPEG file into a regular image file. Jpegtran can perform
various useful transformations on JPEG files: it can make lossless
cropping of JPEG files and lossless pasting of one JPEG into another
(dropping). Rdjpgcom displays any text comments included in a JPEG file.
Wrjpgcom inserts text comments into a JPEG file. Jpegexiforient allow
automatic lossless rotation of JPEG images from a digital camera which
have orientation markings in the EXIF data.

%package -n java-turbojpeg
Summary: Java bindings to the turbojpeg library
Requires: %{turbo} = %{EVRD}
Group: Development/Java

%description -n java-turbojpeg
Java bindings to the turbojpeg library

%prep
%if "%{beta}" != ""
%autosetup -p1 -n %{name}-%{version}-%{beta}
%else
%autosetup -p1
%endif
cp %{SOURCE2} jpegexiforient.c
cp %{SOURCE3} exifautotran

%build
%global optflags %{optflags} -O3 -funroll-loops

mkdir -p jpeg8
pushd jpeg8
%cmake \
%if %{with java}
	-DWITH_JAVA:BOOL=ON \
%endif
	-DWITH_JPEG7:BOOL=ON \
	-DWITH_JPEG8:BOOL=ON \
	-G Ninja \
	../..
%ninja_build
popd

mkdir -p jpeg62
pushd jpeg62
%cmake \
	-DWITH_JPEG7:BOOL=OFF \
	-DWITH_JPEG8:BOOL=OFF \
	-G Ninja \
	../..
%ninja_build
popd

%{__cc} %{optflags} %{ldflags} -o jpegexiforient jpegexiforient.c

#%check
#make -C jpeg8 test
#make -C jpeg62 test

%install
cd jpeg62
%ninja_install -C build

cd ../jpeg8
%ninja_install -C build
cd ..

install -m755 jpegexiforient -D %{buildroot}%{_bindir}/jpegexiforient
install -m755 exifautotran -D %{buildroot}%{_bindir}/exifautotran

#(neoclust) Provide jpegint.h because it is needed by certain software
install -m644 jpegint.h -D %{buildroot}%{_includedir}/jpegint.h

%files -n %{libname}
%{_libdir}/libjpeg.so.%{major}*

%files -n %{libname62}
%{_libdir}/libjpeg.so.%{major62}*

%files -n %{turbo}
%{_libdir}/libturbojpeg.so.%{majorturbo}*

%files -n %{devname}
%doc %{_docdir}/mozjpeg
%{_libdir}/libjpeg.so
%{_libdir}/libturbojpeg.so
%{_includedir}/*.h
%{_libdir}/pkgconfig/*.pc

%files -n %{static}
%{_libdir}/libjpeg.a
%{_libdir}/libturbojpeg.a

%files -n jpeg-progs
%{_bindir}/*
%{_mandir}/man1/*

%if %{with java}
%files -n java-turbojpeg
%{_datadir}/java/turbojpeg.jar
%endif
