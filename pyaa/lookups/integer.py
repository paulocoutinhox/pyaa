from django.db.models import IntegerField, Lookup


class BitwiseAndPresent(Lookup):
    """
    Checks if the specified bit is present (active).
    Generates: (field & value = value)
    """

    lookup_name = "bitand_present"

    def as_sql(self, compiler, connection):
        # process the left-hand side and right-hand side of the query
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        # return the sql for bitwise presence check
        return f"({lhs} & {rhs} = {rhs})", lhs_params + rhs_params * 2


class BitwiseAndNotPresent(Lookup):
    """
    Checks if the specified bit is not present (inactive).
    Generates: (field & value <> value)
    """

    lookup_name = "bitand_not_present"

    def as_sql(self, compiler, connection):
        # process the left-hand side and right-hand side of the query
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        # return the sql for bitwise absence check
        return f"({lhs} & {rhs} <> {rhs})", lhs_params + rhs_params * 2


# register the lookups
IntegerField.register_lookup(BitwiseAndPresent)
IntegerField.register_lookup(BitwiseAndNotPresent)
