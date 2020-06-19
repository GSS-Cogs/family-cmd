import pandas as pd

class Attributes (object):
    """
    A class to allow us to bolt-on required attributes using conditional column item selections.
    """

    def __init__(self, conditions):

        # TODO - validate the conditions somehow,
        # does what's being passed in make sense?

        self.conditions = conditions

    def applied_to(self, df):
        
        columns_to_add = []
        
        for attribute, attr_dict_or_constant in self.conditions.items():
            
            columns_to_add.append(attribute)

            # blow up if we already have a 	column for this attribute
            df[attribute] = ""

            # if its a constant, its easy
            if not isinstance(attr_dict_or_constant, dict):
                df[attribute] = attr_dict_or_constant

            else:
                # If it's a dictionary, only apply the attribute where  all conditions
                # are true (i.e where the expected thing is in the stated columns)

                # Horozontal index of our new attribute column
                x = df.columns.get_loc(attribute)

                for attribute_value, logic_dict in attr_dict_or_constant.items():

                    # temp dataframe to slice and pinch then vertcal index from
                    tdf = df.copy()

                    for column, regex in logic_dict.items():
                        # Todo, use a regex not an exact match
                        tdf = tdf[tdf[column].map(lambda x: regex in x)]

                    # write the attribute into the original dataframe
                    for y in tdf.index.values.tolist():
                        df.iloc[y, x] = attribute_value


            # TODO - also important :)
            # Make sure that any new attribute columns provided are fully populated.
            # ... ideally work out how to pass a flag for this, in case of edge cases
            # where we want a sparse one one day.

        column_order = list(df.columns.values[:1]) + columns_to_add + list(df.columns.values[1:-len(columns_to_add)])
        df = df[column_order]
        
        v4_number = 'v4_' + str(int(df.columns[0].split('_')[-1]) + len(columns_to_add))
        df = df.rename(columns={df.columns[0]:v4_number})
        
        return df
