{% set slang = salt['grains.get']('locale_info:defaultlanguage',) %}
{% set sencode = salt['grains.get']('locale_info:defaultencoding',) %}
{% set puser = salt['pillar.get']('puser',) %}
{% set project = salt['pillar.get']('project',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set sname = salt['pillar.get']('sname',) %}
{% set dname = salt['pillar.get']('dname',) %}
{% set dtime = salt['pillar.get']('dtime',) %}
{% set ifreload = salt['pillar.get']('ifreload',) %}


{% if ifreload == 0 %}
tomcat_shutdown:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}
    - name: |
        source /etc/profile
        source /home/{{ puser }}/.bash_profile
        kill -TERM `cat RUNNING_PID`
        rm -rf RUNNING_PID
    - shell: /bin/bash
    - env:
      - LC_ALL: "{{ slang }}.{{ sencode }}"
    - user: {{ puser }}
{% endif %}

backup_dir:
  file.directory:
    - name: /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}
    - user: {{ puser }}
    - group: {{ puser }}
    - makedirs: True
    - recurse:
      - user
      - group
    {% if ifreload == 0 %}
    - require:
      - tomcat_shutdown
    - onchanges:
      - tomcat_shutdown
    {% endif %}
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}
    - name: /bin/cp -rf {lib,plugins} /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }} && rm -rf {lib,plugins}
    - user: {{ puser }}
    - group: {{ puser }}
    - unless: test ! -d /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}

update_war:
  archive.extracted:
    - name: /home/{{ puser }}/
    - source: salt://full/{{ project }}-{{ dpath }}/{{ dtime }}/{{ sname }}.tar.gz
    - user: {{ puser }}
    - group: {{ puser }}
    - mode: 0664
    - backup: minion
    - require:
      - backup_dir
    - onchanges:
      - backup_dir

{% if ifreload == 0 %}
tomcat_startup:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}
    - name: |
        source /etc/profile
        source /home/{{ puser }}/.bash_profile
        nohup /bin/bash start >/dev/null 2>/dev/null &
    - shell: /bin/bash
    - env:
      - LC_ALL: "{{ slang }}.{{ sencode }}"
    - user: {{ puser }}
    - require:
      - update_war
    - onchanges:
      - update_war
{% endif %}
