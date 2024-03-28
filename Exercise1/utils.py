
def build_aggregate_dictionary(player_columns,player_data_columns) : 
    # creating a dictionary for use in the aggregate function of groupby
    # first is used when we don't want to aggregate but only get the first element
    # sum is used to get the sum of the rows
         agg_dictionary = {}
         player_column_list_first = ['id',	'player_id','season']
        
         for c in list(player_columns):
            agg_dictionary[c]='first'
        
         for c in list(player_data_columns):
           if c not in player_column_list_first:
             agg_dictionary[c]='sum'
           else :
             agg_dictionary[c]='first'

        #adding team_name at the end
         agg_dictionary['team_name'] = 'first'
         return agg_dictionary