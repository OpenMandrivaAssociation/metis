%define	major	0
%define	libname	%mklibname metis %{major}
%define	devname	%mklibname -d metis

Name:		metis
Version:	5.1.0
Release:	7
Summary:	Serial Graph Partitioning and Fill-reducing Matrix Ordering
License:	ASL 2.0 and BSD and LGPLv2+
Group:		System/Libraries
URL:		http://glaros.dtc.umn.edu/gkhome/views/%{name}
Source0:	http://glaros.dtc.umn.edu/gkhome/fetch/sw/%{name}/%{name}-%{version}.tar.gz

## This patch sets up libmetis soname of libmetis
Patch0:		metis-libmetis.patch

## Specify the width (32 or 64 bits) of the elementary data type 
## used in METIS. This is controled by the IDXTYPEWIDTH
## constant.
## For now, on a 32 bit architecture you can only specify a width of 32, 
## whereas for a 64 bit architecture you can specify a width of either 
## 32 or 64 bits.
Patch2:		metis-5.1.0-width-datatype.patch

Patch5:		metis-5.1.0-add-missing-linkage-against-pcreposix.patch

BuildRequires:	cmake

BuildRequires:	gomp-devel
BuildRequires:	pcre-devel
BuildRequires:	help2man

%description
METIS is a set of serial programs for partitioning graphs, 
partitioning finite element meshes, and producing fill reducing 
orderings for sparse matrices. 
The algorithms implemented in METIS are based on the multilevel 
recursive-bisection, multilevel k-way, and multi-constraint 
partitioning schemes developed in our lab.

%package -n	%{libname}
Summary:	Serial Graph Partitioning and Fill-reducing Matrix Ordering
Group:		System/Libraries

%description -n	%{libname}
METIS is a set of serial programs for partitioning graphs, 
partitioning finite element meshes, and producing fill reducing 
orderings for sparse matrices. 
The algorithms implemented in METIS are based on the multilevel 
recursive-bisection, multilevel k-way, and multi-constraint 
partitioning schemes developed in our lab.

%package -n	%{devname}
Summary:	The Metis headers and development-related files
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n	%{devname}
Header and library files of Metis.

%prep
%setup -q
%patch0 -p0

%patch2 -p1 -b .bits~

%patch5 -p1 -b .pcreposix~

%build
%global optflags %{optflags} -O3
%cmake	-DGKLIB_PATH=../GKlib  \
	-DGKRAND:BOOL=ON \
	-DSHARED:BOOL=ON \
	-DPCRE:BOOL=ON \
	-DOPENMP:BOOL=ON
%make

## Generate manpages from binaries
export LD_PRELOAD="$PWD/libmetis/lib%{name}.so.%{major}"

help2man --version-string="%{version}" \
 -n "Partitions a graph into a specified number of parts." \
 -N --output="gpmetis.1" --no-discard-stderr --help-option="-help" programs/gpmetis

help2man --version-string="%{version}" \
 -n "Computes a fill-reducing ordering of the vertices of the graph using multilevel nested dissection." \
 -N --output="ndmetis.1" --no-discard-stderr --help-option="-help" programs/ndmetis

help2man --version-string="%{version}" \
 -n "Partitions a mesh into a specified number of parts." \
 -N --output="mpmetis.1" --no-discard-stderr --help-option="-help" programs/mpmetis

help2man --version-string="%{version}" \
 -n "Converts a mesh into a graph that is compatible with METIS." \
 -N --output="m2gmetis.1" --no-discard-stderr --help-option="-help" programs/m2gmetis

%check
export LD_LIBRARY_PATH="$PWD/build/libmetis"
export PATH="$PWD/build/programs:$PATH"

ndmetis graphs/mdual.graph
mpmetis graphs/metis.mesh 2
gpmetis graphs/test.mgraph 4
gpmetis graphs/copter2.graph 4
graphchk graphs/4elt.graph

%install
%makeinstall_std -C build

install -d %{buildroot}%{_mandir}/man1
cp build/*.1 %{buildroot}%{_mandir}/man1

%files
%doc LICENSE.txt Changelog manual/manual.pdf
%{_bindir}/*
%{_mandir}/man1/*.1*

%files -n %{libname}
%{_libdir}/lib%{name}.so.%{major}*

%files -n %{devname}
%doc Changelog
%{_includedir}/%{name}.h
%{_libdir}/lib%{name}.so

%changelog
* Fri Feb 28 2014 Per Øyvind Karlsen <proyvind@moondrake.org> 5.1.0-3
- initial mdk release

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sun Apr 14 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.1.0-1
- Update to 5.1.0

* Sun Mar 31 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-10
- Removed BR 'perl-Carp' (Bug 926996)
- Added LD_PRELOAD before help2man tasks to fix manpage shared_lib_error

* Sun Mar 24 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-9
- Added BR 'perl-Carp' for Fedora
- Excluded manpage creation for 'cmpfillin' and 'graphchk' commands

* Wed Mar 20 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-8
- Added BR cmake28 for EPEL6 building
- Set up of manpages creation in EPEL6

* Wed Mar 20 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-7
- Removed explicit manpages compression
- License tag changed to 'ASL 2.0 and BSD and LGPLv2+'

* Wed Mar 20 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-6
- Modified %%check section to perform tests properly

* Tue Mar 19 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-5
- Added %%check section
- Removed GK*.h libraries installation

* Sun Mar 17 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-4
- Added patch to sets up GKREGEX, GKRAND, libsuffix options to the Makefiles
- Configured patch2 condition
- soname version of libmetis changed to 0
- Added cmake options and flags to check openmp
- GKlib_includes destination changed to include/metis
- Added commands to generate binaries man-page
- Added BR openmpi-devel, pcre-devel, help2man

* Fri Mar 15 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-3
- Static sub-package removed
- TEMPORARY fix for files in "/usr/lib" removed
- Added patches for set up shared GKlib and soname libmetis 
- Removed BR chrpath

* Thu Mar 14 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-2
- Initial release changed from 0 to 1
- Removed chrpath command
- Added metis-width-datatype.patch only for 64bit systems
- Build commands completely changed to use %%cmake
- TEMPORARY fix for files in "/usr/lib"

* Sat Mar 02 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-1
- Initial package
- Removed chrpaths
- Added BR chrpath
- Removed exec permissions to silence spurious-executable-perm warning
