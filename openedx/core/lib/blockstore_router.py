"""
Database Routers for use with the blockstore django app.
"""


class BlockstoreRouter:
    """
    A Database Router that separates Blockstore into its own database.
    """

    DATABASE_NAME = 'blockstore'

    def db_for_read(self, model, **hints):  # pylint: disable=unused-argument
        """
        Use the BlockstoreRouter.DATABASE_NAME if the model is one of following 
        - Collection
        - Bundle
        - BundleVersion
        - Draft
        - BundleLink
        """
        if model._meta.app_label == 'blockstore':
            return self.DATABASE_NAME
        else:
            return None

    def db_for_write(self, model, **hints):  # pylint: disable=unused-argument
        """
        Use the BlockstoreRouter.DATABASE_NAME if the model is one of following 
        - Collection
        - Bundle
        - BundleVersion
        - Draft
        - BundleLink
        """
        print(model._meta.app_label)
        if model._meta.app_label == 'blockstore':
            return self.DATABASE_NAME
        else:
            return None

    def allow_relation(self, obj1, obj2, **hints):  # pylint: disable=unused-argument
        """
        Manage relations if the model is one of following 
        - Collection
        - Bundle
        - BundleVersion
        - Draft
        - BundleLink
        """
        # Allow relation between CSM and CSMH (this cross-database relationship is declared with db_constraint=False
        # so while cross-model relationship is allowed via Django it is not stored as such within the database).
        # Note: The order of obj1 and obj2 are based on the parent-child relationship as explained in
        #   https://github.com/django/django/blob/stable/2.2.x/django/db/models/fields/related_descriptors.py
        if self._is_csm(obj1) and self._is_csm_h(obj2):
            return True

        # Prevent any other relations with CSMH since CSMH is in its own different database.
        elif self._is_csm_h(obj1) or self._is_csm_h(obj2):
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):  # pylint: disable=unused-argument
        """
        Only sync Blockstore to BlockstoreRouter.DATABASE_Name
        """
        if model_name is not None:
            model = hints.get('model')
            if model is not None and model._meta.app_label == 'blockstore':
                return db == self.DATABASE_NAME
        if db == self.DATABASE_NAME:
            return False

        return None
