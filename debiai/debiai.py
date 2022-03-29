# -*- coding: utf-8 -*-
"""
    DebiAI module for an easy data manipulation with the DebiAI app.

    Author : IRT-SystemX
    Contact : debiai@irt-systemx.fr
    GitHub : git@github.com:DebiAI/py-debiai.git
    Licence : Apache 2.0
"""

from typing import List

import utils as utils
from .debiai_project import Debiai_project


class Debiai:
    """
    Each Debiai object represent a Debiai server instance
    """
    backend_url = None

    def __init__(self, backend_url: str):
        self.backend_url = backend_url
        utils.check_back(backend_url)

    def get_projects(self) -> List[Debiai_project]:
        """
        Return the server existing projects
        """
        projects = []
        projects_list = utils.get_projects(self.backend_url)

        for project in projects_list:
            id = project["id"]
            name = project["name"]
            projects.append(Debiai_project(name, id, self.backend_url))

        return projects

    def get_project(self, project_name: str) -> Debiai_project or None:
        """
        Return a project by name, returns none if the project doesn't exist
        """
        projects_list = utils.get_projects(self.backend_url)

        for project in projects_list:
            id = project["id"]
            name = project["name"]
            if name == project_name:
                return Debiai_project(name, id, self.backend_url)
        return None

    def create_project(self, project_name: str) -> Debiai_project:
        """
        Create a new project from a name
        return the created Debiai_project object
        """
        if project_name is None or project_name == "":
            raise ValueError("Project name cannot be empty")

        project_id = utils.post_project(self.backend_url, project_name)

        return Debiai_project(project_name, project_id, self.backend_url)

    def delete_project(self, project: Debiai_project) -> bool:
        """
        Remove a project from the server
        """
        return utils.delete_project(self.backend_url, project.id)

    def delete_project_byId(self, projectId: str) -> bool:
        """
        Remove a project from the server
        """
        return utils.delete_project(self.backend_url, projectId)
