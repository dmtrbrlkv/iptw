%define _python_bytecompile_errors_terminate_build 0

License:        BSD
Vendor:         Otus
Group:          PD01
URL:            http://otus.ru/lessons/3/
Source:         otus-%{current_datetime}.tar.gz
BuildRoot:      %{_tmppath}/otus-%{current_datetime}
Name:           ip2w
Version:        0.0.1
Release:        1
BuildArch:      noarch
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
Requires:       epel-release
Requires:       python3, python3-devel, gcc, nginx
Summary:  IP to weather daemon


%description
The daemon returns the weather in json format in the city determined by the transmitted addresss
Git version: %{git_version} (branch: %{git_branch})

%define __etcdir    /usr/local/etc/
%define __logdir    /var/log/ip2w
%define __bindir    /usr/local/ip2w/
%define __systemddir	/usr/lib/systemd/system/

%prep
%setup -c

%install
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}
%{__mkdir} -p %{buildroot}/%{__systemddir}
%{__mkdir} -p %{buildroot}/%{__bindir}
%{__mkdir} -p %{buildroot}/%{__etcdir}
%{__mkdir} -p %{buildroot}/%{__logdir}

%{__install} -pD -m 755 otus-%{current_datetime}/ip2w.py %{buildroot}/%{__bindir}
%{__install} -pD -m 644 otus-%{current_datetime}/ip2w.json %{buildroot}/%{__etcdir}
%{__install} -pD -m 644 otus-%{current_datetime}/ip2w.ini %{buildroot}/%{__etcdir}

%{__install} -pD -m 644 otus-%{current_datetime}/uwsgi.service %{buildroot}/%{__systemddir}/%{name}.service


%post
%systemd_post %{name}.service
systemctl daemon-reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%clean
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}


%files
%config %{__etcdir}/ip2w.ini
%config %{__etcdir}/ip2w.json
%{__bindir}
%{__logdir}
%{__systemddir}

