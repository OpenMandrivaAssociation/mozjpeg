%define major 8
%define majorturbo 0
%define libname %mklibname jpeg %{major}
%define devname %mklibname -d jpeg
%define static %mklibname -s -d jpeg
%define turbo %mklibname turbojpeg %{majorturbo}

%define major62 62
%define libname62 %mklibname jpeg %{major62}

Summary:	A MMX/SSE2 accelerated library for manipulating JPEG image files
Name:		mozjpeg
Epoch:		1
Version:	3.1
Release:	8
License:	wxWidgets Library License
Group:		System/Libraries
Url:		https://github.com/mozilla/mozjpeg
Source0:	https://github.com/mozilla/mozjpeg/archive/v%{version}.tar.gz
# These two allow automatic lossless rotation of JPEG images from a digital
# camera which have orientation markings in the EXIF data. After rotation
# the orientation markings are reset to avoid duplicate rotation when
# applying these programs again.
Source2:	http://jpegclub.org/jpegexiforient.c
Source3:	http://jpegclub.org/exifautotran.txt
Patch0:		jpeg-6b-c++fixes.patch
# (tpg) fix crashes https://github.com/mozilla/mozjpeg/issues/202
Patch1:		0000-Fix-x86-64-ABI-conformance-issue-in-SIMD-code.patch
BuildRequires:	libtool >= 1.4
BuildRequires:	pkgconfig(libpng)
%ifarch %{ix86} x86_64
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

%prep
%setup -q
%patch0 -p0
%patch1 -p1

# Fix perms
chmod -x README-turbo.txt

cp %{SOURCE2} jpegexiforient.c
cp %{SOURCE3} exifautotran

autoheader
libtoolize --force
aclocal
automake -a
autoconf

%build
%global optflags %{optflags} -Ofast -funroll-loops

# fix me on RPM
for i in $(find . -name config.guess -o -name config.sub) ; do
    [ -f /usr/share/libtool/config/$(basename $i) ] && /bin/rm -f $i && /bin/cp -fv /usr/share/libtool/config//$(basename $i) $i ;
done;
# and remove me

CONFIGURE_TOP="$PWD"

mkdir -p jpeg8
pushd jpeg8

%configure \
	--enable-shared \
	--enable-static \
	--with-jpeg8
%make
popd

mkdir -p jpeg62
pushd jpeg62

%configure \
	--enable-shared \
	--disable-static
%make
popd

gcc %{optflags} %{ldflags} -o jpegexiforient jpegexiforient.c

#%check
#make -C jpeg8 test
#make -C jpeg62 test

%install
make install-libLTLIBRARIES DESTDIR=%{buildroot} -C jpeg62
%makeinstall_std -C jpeg8

install -m755 jpegexiforient -D %{buildroot}%{_bindir}/jpegexiforient
install -m755 exifautotran -D %{buildroot}%{_bindir}/exifautotran

#(neoclust) Provide jpegint.h because it is needed by certain software
install -m644 jpegint.h -D %{buildroot}%{_includedir}/jpegint.h

# cleanup
rm -f %{buildroot}%{_docdir}/*

%files -n %{libname}
%{_libdir}/libjpeg.so.%{major}*

%files -n %{libname62}
%{_libdir}/libjpeg.so.%{major62}*

%files -n %{turbo}
%{_libdir}/libturbojpeg.so.%{majorturbo}*

%files -n %{devname}
%doc coderules.txt example.c jconfig.txt libjpeg.txt structure.txt
%doc change.log ChangeLog.txt README README-turbo.txt
%{_libdir}/libjpeg.so
%{_libdir}/libturbojpeg.so
%{_includedir}/*.h

%files -n %{static}
%{_libdir}/libjpeg.a
%{_libdir}/libturbojpeg.a

%files -n jpeg-progs
%doc usage.txt wizard.txt
%{_bindir}/*
%{_mandir}/man1/*
