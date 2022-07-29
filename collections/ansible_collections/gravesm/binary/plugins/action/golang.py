import os
import subprocess

from ansible.collections.list import list_collection_dirs
from ansible.plugins.action import ActionBase


ARCH_MAPPINGS = {
    "x86_64": "amd64",
}


def get_platform(system, arch):
    os = system.lower()
    arch = ARCH_MAPPINGS.get(arch, arch)
    return os, arch


def build_module(action, system, arch):
    collection, module = action.rsplit(".", maxsplit=1)
    collection_path = list(list_collection_dirs(coll_filter=collection))[0]
    module_path = "plugins/modules/{}_{}_{}".format(module, system, arch)
    source_path = "./cmd/{0}".format(module)
    build = ["go", "build", "-o", module_path, source_path]
    env = os.environ.copy()
    env["GOOS"] = system
    env["GOARCH"] = arch
    res = subprocess.run(build, env=env, cwd=collection_path)
    res.check_returncode()


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        os, arch = get_platform(
            task_vars.get("ansible_system"),
            task_vars.get("ansible_architecture"))
        build_module(self._task.action, os, arch)
        module_args = self._task.args.copy()
        return self._execute_module(module_name="{}_{}_{}".format(self._task.action, os, arch),
                                    module_args=module_args,
                                    task_vars=task_vars, tmp=tmp)
