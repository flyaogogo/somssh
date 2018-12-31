{% set slang = salt['grains.get']('locale_info:defaultlanguage',) %}
{% set sencode = salt['grains.get']('locale_info:defaultencoding',) %}
{% set puser = salt['pillar.get']('puser',) %}
{% set project = salt['pillar.get']('project',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set spath = salt['pillar.get']('spath',) %}
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
    - name: /home/{{ puser }}/backup/increase/{{ dpath }}/{{ spath }}/
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
    - name: /bin/cp -rf /home/{{ puser }}/{{ dpath }}/{{ dname }}/* /home/{{ puser }}/backup/increase/{{ dpath }}/{{ spath }}/
    - user: {{ puser }}
    - group: {{ puser }}
    - unless: test ! -d /home/{{ puser }}/backup/increase/{{ dpath }}/{{ spath }}/

update_war:
  file.recurse:
    - name: /home/{{ puser }}/{{ dpath }}/{{ dname }}
    - user: {{ puser }}
    - group: {{ puser }}
    #- dir_mode: 2755
    - source: salt://increase/{{ project }}-{{ dpath }}/{{ spath }}
    - include_empty: True
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
