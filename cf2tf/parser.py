"""
CloudFormation Template Parser

Parses AWS CloudFormation templates in YAML or JSON format and extracts
all resources, parameters, outputs, mappings, and conditions.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


class CloudFormationIntrinsicResolver:
    """Handles CloudFormation intrinsic functions."""

    INTRINSIC_FUNCTIONS = {
        "Ref": "ref",
        "Fn::GetAtt": "getatt",
        "Fn::Join": "join",
        "Fn::Sub": "sub",
        "Fn::If": "if",
        "Fn::Equals": "equals",
        "Fn::And": "and",
        "Fn::Or": "or",
        "Fn::Not": "not",
        "Fn::Condition": "condition",
        "Fn::Base64": "base64",
        "Fn::Cidr": "cidr",
        "Fn::FindInMap": "findinmap",
        "Fn::GetAZs": "getazs",
        "Fn::ImportValue": "importvalue",
        "Fn::Select": "select",
        "Fn::Split": "split",
        "Fn::Transform": "transform",
    }

    @classmethod
    def identify_intrinsic(cls, value: Any) -> Optional[str]:
        """Identify if a value contains an intrinsic function."""
        if isinstance(value, dict):
            for key in value.keys():
                if key in cls.INTRINSIC_FUNCTIONS:
                    return key
                if key.startswith("!"):
                    return key
        return None

    @classmethod
    def parse_intrinsic(cls, value: Any) -> Dict[str, Any]:
        """Parse an intrinsic function and return structured data."""
        if not isinstance(value, dict):
            return {"type": "literal", "value": value}

        intrinsic = cls.identify_intrinsic(value)
        if not intrinsic:
            return {"type": "literal", "value": value}

        func_name = cls.INTRINSIC_FUNCTIONS.get(intrinsic, intrinsic.lstrip("!").lower())
        func_value = value[intrinsic]

        return {
            "type": "intrinsic",
            "function": func_name,
            "value": func_value,
            "original": value,
        }


class CloudFormationParser:
    """
    Parses CloudFormation templates and extracts structured information.

    Supports both YAML and JSON formats, including CloudFormation-specific
    YAML tags like !Ref, !GetAtt, etc.
    """

    def __init__(self, template_path: Optional[str] = None, template_content: Optional[str] = None):
        """
        Initialize the parser with a template file or content.

        Args:
            template_path: Path to the CloudFormation template file
            template_content: Raw template content as string
        """
        self.template_path = template_path
        self.template_content = template_content
        self.template: Dict[str, Any] = {}
        self.resources: Dict[str, Any] = {}
        self.parameters: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}
        self.mappings: Dict[str, Any] = {}
        self.conditions: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.globals: Dict[str, Any] = {}
        self.transform: Optional[str] = None

    def _create_yaml_loader(self):
        """Create a YAML loader that handles CloudFormation intrinsic functions."""
        loader = yaml.SafeLoader

        # Define constructors for CloudFormation intrinsic functions
        def create_intrinsic_constructor(tag_name):
            def constructor(loader, node):
                if isinstance(node, yaml.ScalarNode):
                    value = loader.construct_scalar(node)
                elif isinstance(node, yaml.SequenceNode):
                    value = loader.construct_sequence(node)
                elif isinstance(node, yaml.MappingNode):
                    value = loader.construct_mapping(node)
                else:
                    value = None
                return {tag_name: value}
            return constructor

        # Register all CloudFormation intrinsic function tags
        intrinsic_tags = [
            ("!Ref", "Ref"),
            ("!GetAtt", "Fn::GetAtt"),
            ("!Join", "Fn::Join"),
            ("!Sub", "Fn::Sub"),
            ("!If", "Fn::If"),
            ("!Equals", "Fn::Equals"),
            ("!And", "Fn::And"),
            ("!Or", "Fn::Or"),
            ("!Not", "Fn::Not"),
            ("!Condition", "Fn::Condition"),
            ("!Base64", "Fn::Base64"),
            ("!Cidr", "Fn::Cidr"),
            ("!FindInMap", "Fn::FindInMap"),
            ("!GetAZs", "Fn::GetAZs"),
            ("!ImportValue", "Fn::ImportValue"),
            ("!Select", "Fn::Select"),
            ("!Split", "Fn::Split"),
            ("!Transform", "Fn::Transform"),
        ]

        for yaml_tag, cfn_function in intrinsic_tags:
            yaml.add_constructor(yaml_tag, create_intrinsic_constructor(cfn_function), loader)

        return loader

    def parse(self) -> Dict[str, Any]:
        """
        Parse the CloudFormation template.

        Returns:
            Dictionary containing parsed template data
        """
        content = self._load_template()
        self.template = self._parse_content(content)
        self._extract_sections()

        return {
            "template": self.template,
            "resources": self.resources,
            "parameters": self.parameters,
            "outputs": self.outputs,
            "mappings": self.mappings,
            "conditions": self.conditions,
            "metadata": self.metadata,
            "transform": self.transform,
        }

    def _load_template(self) -> str:
        """Load template content from file or use provided content."""
        if self.template_content:
            return self.template_content

        if self.template_path:
            path = Path(self.template_path)
            if not path.exists():
                raise FileNotFoundError(f"Template file not found: {self.template_path}")
            return path.read_text(encoding="utf-8")

        raise ValueError("Either template_path or template_content must be provided")

    def _parse_content(self, content: str) -> Dict[str, Any]:
        """Parse template content as YAML or JSON."""
        # Try JSON first (it's stricter)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try YAML with CloudFormation intrinsic function support
        try:
            loader = self._create_yaml_loader()
            return yaml.load(content, Loader=loader)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse template as YAML or JSON: {e}")

    def _extract_sections(self):
        """Extract all sections from the parsed template."""
        self.resources = self.template.get("Resources", {})
        self.parameters = self.template.get("Parameters", {})
        self.outputs = self.template.get("Outputs", {})
        self.mappings = self.template.get("Mappings", {})
        self.conditions = self.template.get("Conditions", {})
        self.metadata = self.template.get("Metadata", {})
        self.globals = self.template.get("Globals", {})
        self.transform = self.template.get("Transform")

    def get_resource_types(self) -> List[str]:
        """Get a list of all resource types in the template."""
        return list(set(
            resource.get("Type", "Unknown")
            for resource in self.resources.values()
        ))

    def get_resource_by_type(self, resource_type: str) -> Dict[str, Any]:
        """Get all resources of a specific type."""
        return {
            name: resource
            for name, resource in self.resources.items()
            if resource.get("Type") == resource_type
        }

    def get_dependencies(self, resource_name: str) -> List[str]:
        """Get explicit and implicit dependencies for a resource."""
        if resource_name not in self.resources:
            return []

        resource = self.resources[resource_name]
        dependencies = set()

        # Explicit DependsOn
        depends_on = resource.get("DependsOn", [])
        if isinstance(depends_on, str):
            depends_on = [depends_on]
        dependencies.update(depends_on)

        # Implicit dependencies from Ref and GetAtt
        self._find_references(resource, dependencies)

        return list(dependencies)

    def _find_references(self, obj: Any, references: set):
        """Recursively find all resource references in an object."""
        if isinstance(obj, dict):
            if "Ref" in obj:
                ref = obj["Ref"]
                if ref in self.resources:
                    references.add(ref)
            if "Fn::GetAtt" in obj:
                getatt = obj["Fn::GetAtt"]
                if isinstance(getatt, list) and len(getatt) >= 1:
                    if getatt[0] in self.resources:
                        references.add(getatt[0])
                elif isinstance(getatt, str):
                    parts = getatt.split(".")
                    if parts[0] in self.resources:
                        references.add(parts[0])

            for value in obj.values():
                self._find_references(value, references)

        elif isinstance(obj, list):
            for item in obj:
                self._find_references(item, references)

    def validate_template(self) -> List[Dict[str, str]]:
        """
        Perform basic validation on the template.

        Returns:
            List of validation issues found
        """
        issues = []

        # Check for required sections
        if not self.resources:
            issues.append({
                "severity": "error",
                "message": "Template has no Resources section",
                "location": "Resources",
            })

        # Check for valid resource types
        for name, resource in self.resources.items():
            if "Type" not in resource:
                issues.append({
                    "severity": "error",
                    "message": f"Resource '{name}' has no Type defined",
                    "location": f"Resources.{name}",
                })

        # Check for circular dependencies
        for name in self.resources:
            if self._has_circular_dependency(name, set()):
                issues.append({
                    "severity": "error",
                    "message": f"Circular dependency detected involving resource '{name}'",
                    "location": f"Resources.{name}",
                })

        return issues

    def _has_circular_dependency(self, resource_name: str, visited: set) -> bool:
        """Check if a resource has circular dependencies."""
        if resource_name in visited:
            return True

        visited.add(resource_name)
        for dep in self.get_dependencies(resource_name):
            if self._has_circular_dependency(dep, visited.copy()):
                return True

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert parsed template to a dictionary."""
        return {
            "format_version": self.template.get("AWSTemplateFormatVersion", "2010-09-09"),
            "description": self.template.get("Description", ""),
            "transform": self.transform,
            "parameters": self.parameters,
            "mappings": self.mappings,
            "conditions": self.conditions,
            "resources": self.resources,
            "outputs": self.outputs,
            "metadata": self.metadata,
        }
