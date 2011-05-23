# coding: utf-8
#
# Copyright 2010 Alexandre Fiori
# based on the original Tornado by Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import base64
import getopt
import os
import re
import string
import sys
import uuid
import zipfile

def new_project(**kwargs):
    zf = kwargs["skel"]
    dst = kwargs["project_path"]

    os.mkdir(dst, 0755)
    for n in zf.namelist():
        mod = n.replace("modname", kwargs["modname"])
        if n[-1] in (os.path.sep, "\\", "/"):
            os.mkdir(os.path.join(dst, mod), 0755)
        else:
            ext = n.rsplit(".", 1)[-1]
            fd = open(os.path.join(dst, mod), "w", 0644)
            if ext in ("conf", "html", "py", "rst"):
                fd.write(string.Template(zf.read(n)).substitute(kwargs))
            else:
                fd.write(zf.read(n))
            fd.close()

    if kwargs["use_git"] is True:
        os.chdir(kwargs["project_path"])
        os.system("git init")
        os.system("git add .gitignore")


def usage(version, target):
    print("""
use: %s [options]
Options:
 -h --help              Show this help.
 -g --git               Use git's name and email settings, and create a git repo on target
 -p --project=NAME      Create new cyclone project.
 -m --modname=NAME      Use another name for the module [default: project_name]
 -v --version=VERSION   Set project version [default: %s]
 -s --set-pkg-version   Set version on package name [default: False]
 -t --target=PATH       Set path where project is created [default: %s]
    """ % (sys.argv[0], version, target))
    sys.exit(0)


if __name__ == "__main__":
    project = None
    modname = None
    use_git = False
    set_pkg_version = False
    default_version, version = "0.1", None
    default_target, target = os.getcwd(), None

    short = "hgsp:m:v:t:"
    long  = ["help", "git", "set-pkg-version", "project=", "modname=", "version=", "target="]
    try:
        opts, args = getopt.getopt(sys.argv[1:], short, long)
    except getopt.GetoptError, err:
        usage(default_version, default_target)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage(default_version, default_target)

        if o in ("-g", "--git"):
            use_git = True

        if o in ("-s", "--set-pkg-version"):
            set_pkg_version = True

        elif o in ("-p", "--project"):
            project = a

        elif o in ("-m", "--modname"):
            modname = a

        elif o in ("-v", "--version"):
            version = a

        elif o in ("-t", "--target"):
            target = a

    if project is None:
        usage(default_version, default_target)
    elif not re.match(r"^[0-9a-z][0-9a-z_-]+$", project, re.I):
        print("Invalid project name.")
        sys.exit(1)

    mod_is_proj = False
    if modname is None:
        mod_is_proj = True
        modname = project

    if modname in ("frontend", "tools", "twisted"):
        if mod_is_proj is True:
            print("Please specify a different modname, using --modname=name. '%s' is not allowed." % modname)
        else:
            print("Please specify a different modname. '%s' is not allowed." % modname)
        sys.exit(1)

    if not re.match(r"^[0-9a-z_]+$", modname, re.I):
        print("Invalid module name.")
        sys.exit(1)

    if version is None:
        version = default_version

    if target is None:
        target = default_target

    if not (os.access(target, os.W_OK) and os.access(target, os.X_OK)):
        print("Cannot create project on target directory '%s': permission denied" % target)
        sys.exit(1)

    name = "Foo Bar"
    email = "root@localhost"
    if use_git is True:
        with os.popen("git config --list") as fd:
            for line in fd:
                line = line.replace("\r", "").replace("\n", "")
                try:
                    k, v = line.split("=", 1)
                except:
                    continue

                if k == "user.name":
                    name = v
                elif k == "user.email":
                    email = v

    skel = zipfile.ZipFile(open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "appskel.zip")))

    if set_pkg_version is True:
        project_name="%s-%s" % (project, version)
    else:
        project_name=project
    project_path=os.path.join(target, project_name)
    new_project(
        skel=skel,
        name=name,
        email=email,
        project=project,
        project_name=project_name,
        project_path=project_path,
        modname=modname,
        version=version,
        target=target,
        use_git=use_git,
        locale_path=os.path.join(project_path, "frontend", "locale"),
        static_path=os.path.join(project_path, "frontend", "static"),
        template_path=os.path.join(project_path, "frontend", "template"),
        cookie_secret=base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
        )
