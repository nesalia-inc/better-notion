"""Unit tests for role-based access control (RBAC)."""

import pytest

from better_notion.utils.agents.rbac import RoleManager


class TestRoleManager:
    """Tests for RoleManager class."""

    def test_developer_can_claim_tasks(self) -> None:
        """Test that Developer can claim tasks."""
        assert RoleManager.check_permission("Developer", "tasks:claim") is True

    def test_developer_can_complete_tasks(self) -> None:
        """Test that Developer can complete tasks."""
        assert RoleManager.check_permission("Developer", "tasks:complete") is True

    def test_developer_cannot_create_projects(self) -> None:
        """Test that Developer cannot create projects."""
        assert RoleManager.check_permission("Developer", "projects:create") is False

    def test_developer_can_submit_ideas(self) -> None:
        """Test that Developer can submit ideas."""
        assert RoleManager.check_permission("Developer", "ideas:submit") is True

    def test_developer_cannot_review_ideas(self) -> None:
        """Test that Developer cannot review ideas."""
        assert RoleManager.check_permission("Developer", "ideas:review") is False

    def test_pm_has_full_task_access(self) -> None:
        """Test that PM has full task access."""
        assert RoleManager.check_permission("PM", "tasks:claim") is True
        assert RoleManager.check_permission("PM", "tasks:start") is True
        assert RoleManager.check_permission("PM", "tasks:complete") is True
        assert RoleManager.check_permission("PM", "tasks:delete") is True

    def test_pm_can_create_projects(self) -> None:
        """Test that PM can create projects."""
        assert RoleManager.check_permission("PM", "projects:create") is True

    def test_pm_can_review_ideas(self) -> None:
        """Test that PM can review ideas."""
        assert RoleManager.check_permission("PM", "ideas:review") is True

    def test_pm_can_view_analytics(self) -> None:
        """Test that PM can view analytics."""
        assert RoleManager.check_permission("PM", "analytics:view") is True

    def test_product_analyst_can_view_projects(self) -> None:
        """Test that Product Analyst can view projects."""
        assert RoleManager.check_permission("Product Analyst", "projects:view") is True

    def test_product_analyst_cannot_create_projects(self) -> None:
        """Test that Product Analyst cannot create projects."""
        assert RoleManager.check_permission("Product Analyst", "projects:create") is False

    def test_product_analyst_cannot_claim_tasks(self) -> None:
        """Test that Product Analyst cannot claim tasks."""
        assert RoleManager.check_permission("Product Analyst", "tasks:claim") is False

    def test_product_analyst_can_view_analytics(self) -> None:
        """Test that Product Analyst can view analytics."""
        assert RoleManager.check_permission("Product Analyst", "analytics:view") is True

    def test_qa_can_review_tasks(self) -> None:
        """Test that QA can review tasks."""
        assert RoleManager.check_permission("QA", "tasks:review") is True

    def test_qa_cannot_claim_tasks(self) -> None:
        """Test that QA cannot claim tasks."""
        assert RoleManager.check_permission("QA", "tasks:claim") is False

    def test_qa_can_create_incidents(self) -> None:
        """Test that QA can create incidents."""
        assert RoleManager.check_permission("QA", "incidents:create") is True

    def test_qa_can_resolve_incidents(self) -> None:
        """Test that QA can resolve incidents."""
        assert RoleManager.check_permission("QA", "incidents:resolve") is True

    def test_designer_can_claim_tasks(self) -> None:
        """Test that Designer can claim tasks."""
        assert RoleManager.check_permission("Designer", "tasks:claim") is True

    def test_designer_cannot_create_projects(self) -> None:
        """Test that Designer cannot create projects."""
        assert RoleManager.check_permission("Designer", "projects:create") is False

    def test_devops_can_create_infrastructure_tasks(self) -> None:
        """Test that DevOps can create infrastructure tasks."""
        assert (
            RoleManager.check_permission("DevOps", "tasks:create:infrastructure") is True
        )

    def test_devops_can_create_deployment_tasks(self) -> None:
        """Test that DevOps can create deployment tasks."""
        assert RoleManager.check_permission("DevOps", "tasks:create:deployment") is True

    def test_devops_can_manage_incidents(self) -> None:
        """Test that DevOps has full incident access."""
        assert RoleManager.check_permission("DevOps", "incidents:create") is True
        assert RoleManager.check_permission("DevOps", "incidents:resolve") is True
        assert RoleManager.check_permission("DevOps", "incidents:delete") is True

    def test_admin_has_all_permissions(self) -> None:
        """Test that Admin has all permissions."""
        assert RoleManager.check_permission("Admin", "tasks:claim") is True
        assert RoleManager.check_permission("Admin", "projects:create") is True
        assert RoleManager.check_permission("Admin", "organizations:delete") is True
        assert RoleManager.check_permission("Admin", "random:permission") is True

    def test_invalid_role_has_no_permissions(self) -> None:
        """Test that an invalid role has no permissions."""
        assert RoleManager.check_permission("InvalidRole", "tasks:claim") is False

    def test_require_permission_granted(self) -> None:
        """Test require_permission when permission is granted."""
        # Should not raise
        RoleManager.require_permission("Developer", "tasks:claim")

    def test_require_permission_denied(self) -> None:
        """Test require_permission when permission is denied."""
        with pytest.raises(PermissionError) as exc_info:
            RoleManager.require_permission("Developer", "projects:create")

        assert "does not have permission" in str(exc_info.value)

    def test_get_permissions_developer(self) -> None:
        """Test getting permissions for Developer role."""
        perms = RoleManager.get_permissions("Developer")

        assert "tasks:claim" in perms
        assert "ideas:submit" in perms
        assert len(perms) > 0

    def test_get_permissions_invalid_role(self) -> None:
        """Test getting permissions for invalid role."""
        perms = RoleManager.get_permissions("InvalidRole")

        assert perms == []

    def test_get_all_roles(self) -> None:
        """Test getting all defined roles."""
        roles = RoleManager.get_all_roles()

        assert "Developer" in roles
        assert "PM" in roles
        assert "QA" in roles
        assert "Admin" in roles
        assert len(roles) == 7

    def test_is_valid_role_true(self) -> None:
        """Test is_valid_role with valid role."""
        assert RoleManager.is_valid_role("Developer") is True
        assert RoleManager.is_valid_role("PM") is True
        assert RoleManager.is_valid_role("Admin") is True

    def test_is_valid_role_false(self) -> None:
        """Test is_valid_role with invalid role."""
        assert RoleManager.is_valid_role("InvalidRole") is False
        assert RoleManager.is_valid_role("") is False
        assert RoleManager.is_valid_role("developer") is False  # Case sensitive

    def test_get_role_description_developer(self) -> None:
        """Test getting role description for Developer."""
        desc = RoleManager.get_role_description("Developer")

        assert desc is not None
        assert "tasks" in desc.lower()

    def test_get_role_description_invalid(self) -> None:
        """Test getting role description for invalid role."""
        desc = RoleManager.get_role_description("InvalidRole")

        assert desc is None

    def test_wildcard_permission_matching(self) -> None:
        """Test that wildcard permissions match correctly."""
        # PM has tasks:*
        assert RoleManager.check_permission("PM", "tasks:claim") is True
        assert RoleManager.check_permission("PM", "tasks:delete") is True
        assert RoleManager.check_permission("PM", "tasks:any-action") is True

    def test_resource_specific_wildcard(self) -> None:
        """Test resource-specific wildcard permissions."""
        # DevOps has incidents:*
        assert RoleManager.check_permission("DevOps", "incidents:create") is True
        assert RoleManager.check_permission("DevOps", "incidents:update") is True
        assert RoleManager.check_permission("DevOps", "incidents:delete") is True

    def test_action_specific_wildcard(self) -> None:
        """Test action-specific wildcard permissions."""
        # DevOps has tasks:create:*
        assert RoleManager.check_permission("DevOps", "tasks:create:infrastructure") is True
        assert RoleManager.check_permission("DevOps", "tasks:create:deployment") is True
        # But not other actions
        assert RoleManager.check_permission("DevOps", "tasks:update:infrastructure") is False

    def test_designer_cannot_create_non_design_tasks(self) -> None:
        """Test that Designer can only create design tasks."""
        # Designer should NOT be able to create generic tasks
        assert RoleManager.check_permission("Designer", "tasks:create") is False
        # Or other task types
        assert RoleManager.check_permission("Designer", "tasks:create:infrastructure") is False

    def test_case_sensitive_roles(self) -> None:
        """Test that roles are case-sensitive."""
        assert RoleManager.is_valid_role("Developer") is True
        assert RoleManager.is_valid_role("developer") is False
        assert RoleManager.is_valid_role("DEVELOPER") is False

    def test_case_sensitive_permissions(self) -> None:
        """Test that permissions are case-sensitive."""
        assert RoleManager.check_permission("Developer", "tasks:claim") is True
        assert RoleManager.check_permission("Developer", "Tasks:Claim") is False
        assert RoleManager.check_permission("Developer", "tasks:Claim") is False
