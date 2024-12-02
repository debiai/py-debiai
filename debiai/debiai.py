# -*- coding: utf-8 -*-
"""
    DebiAI module for an easy data manipulation with the DebiAI app.

    Author : IRT-SystemX
    Contact : debiai@irt-systemx.fr
    GitHub : git@github.com:DebiAI/py-debiai.git
    License : Apache 2.0
"""

from typing import List, Union

import utils as utils
from .debiai_project import Debiai_project


class Debiai:
    """
    Each Debiai object represent a Debiai server instance
    """

    debiai_url = ""

    def __init__(self, debiai_url: str):
        self.debiai_url = debiai_url.strip()

        # Check if the url is valid
        if self.debiai_url is None or self.debiai_url == "":
            raise ValueError("Backend url cannot be empty")

        # Remove #
        self.debiai_url = self.debiai_url.removesuffix("#")

        # Remove trailing slash
        self.debiai_url = self.debiai_url.rstrip("/")

        # Remove empty space
        self.debiai_url = self.debiai_url.removesuffix(" ")

        # Remove trailing slash then space
        self.debiai_url = self.debiai_url.replace("/ ", "")

        # Remove trailing space then slash
        self.debiai_url = self.debiai_url.replace(" /", "")

        # Remove trailing slash, sharp then slash
        self.debiai_url = self.debiai_url.rstrip("/#/")

        # Check if the url is in uppercase
        self.debiai_url = self.debiai_url.lower()

        utils.check_back(self.debiai_url)

    def get_projects(self) -> List[Debiai_project]:
        """
        Return the server existing projects
        """
        projects = []
        projects_list = utils.get_projects(self.debiai_url)

        for project in projects_list:
            id = project["id"]
            name = project["name"]
            projects.append(Debiai_project(name, id, self.debiai_url))

        return projects

    def get_project(self, project_id: str) -> Union[Debiai_project, None]:
        """
        Return a project by name, returns none if the project doesn't exist
        """
        project = utils.get_project(self.debiai_url, project_id)
        if project:
            return Debiai_project(project["name"], project_id, self.debiai_url)
        else:
            return None

    def create_project(self, project_name: str) -> Debiai_project:
        """
        Create a new project from a name
        return the created Debiai_project object
        """
        if project_name is None or project_name == "":
            raise ValueError("Project name cannot be empty")

        project_id = utils.post_project(self.debiai_url, project_name)

        return Debiai_project(project_name, project_id, self.debiai_url)

    def delete_project(self, project: Debiai_project) -> bool:
        """
        Remove a project from the server
        """
        if project is None:
            raise ValueError("Project cannot be None")
        if type(project) is not Debiai_project:
            raise ValueError(
                "Parameter must be a Debiai_project object, not a "
                + type(project).__name__
                + ", use delete_project_byId instead"
            )

        return utils.delete_project(self.debiai_url, project.id)

    def delete_project_byId(self, projectId: str) -> bool:
        """
        Remove a project from the server
        """
        if projectId is None or projectId == "":
            raise ValueError("Project ID cannot be empty")
        if type(projectId) is not str:
            raise ValueError("Project ID must be a string")
        return utils.delete_project(self.debiai_url, projectId)
