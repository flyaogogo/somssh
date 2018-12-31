{% set slang = salt['grains.get']('locale_info:defaultlanguage',) %}
{% set sencode = salt['grains.get']('locale_info:defaultencoding',) %}
{% set puser = salt['pillar.get']('puser',) %}
{% set project = salt['pillar.get']('project',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set sname = salt['pillar.get']('sname',) %}
{% set dname = salt['pillar.get']('dname',) %}
{% set dtime = salt['pillar.get']('dtime',) %}
{% set ifreload = salt['pillar.get']('ifreload',) %}


backup_dir:
  file.directory:
    - name: /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}
    - user: {{ puser }}
    - group: {{ puser }}
    - makedirs: True
    - recurse:
      - user
      - group

  cmd.run:
    - cwd: /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}
    - name: /bin/cp -rf /home/{{ puser }}/{{ dpath }}/webapps/{{ dname }}* .
    - user: {{ puser }}
    - group: {{ puser }}
    - shell: /bin/bash
    - env:
      - LC_ALL: "{{ slang }}.{{ sencode }}"
    - unless: test ! -d /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}

update_war:
  file.managed:
    - name: /home/{{ puser }}/{{ dpath }}/webapps/{{ dname }}.war
    - source: salt://full/{{ project }}-{{ dpath }}/{{ dtime }}/{{ sname }}.war
    - user: {{ puser }}
    - group: {{ puser }}
    - mode: 644
    - backup: minion
    - require:
      - backup_dir
    - onchanges:
      - backup_dir

{% if ifreload == 0 %}
tomcat_shutdown:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}
    - name: |
        source /etc/profile
        source /home/{{ puser }}/.bash_profile
        p=`ps ax|grep /home/{{ puser }}/{{ dpath }}/bin/|grep -v 'grep'|awk '{print $1}'`
        [ -z $p ] || (echo "Process kill now..." && kill -9 $p)
        [ -f PID ] && rm -rf PID
        rm -rf /home/{{ puser }}/{{ dpath }}/webapps/{{ dname }}
        rm -rf /home/{{ puser }}/{{ dpath }}/webapps/ROOT
        rm -rf /home/{{ puser }}/{{ dpath }}/work/Catalina/localhost
    - shell: /bin/bash
    - env:
      - LC_ALL: "{{ slang }}.{{ sencode }}"
    - user: {{ puser }}
    - require:
      - update_war
    - onchanges:
      - update_war

tomcat_startup:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}/bin
    - name: |
        source /etc/profile
        source /home/{{ puser }}/.bash_profile
        /bin/bash startup.sh
    - shell: /bin/bash
    - env:
      - LC_ALL: "{{ slang }}.{{ sencode }}"
    - user: {{ puser }}
    - require:
      - tomcat_shutdown
    - onchanges:
      - tomcat_shutdown
{% endif %}
