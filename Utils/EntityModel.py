import pandas as pd

class EntityModel():


	def __init__(self, file):
		self.HIERARCHY_DICT = {
		    ('1','0'): "G-ULTIMATE",
		    ('1','3'): "SUBSIDIARY",
		    ('2','0'): "BRANCH",
		    ('0','3'): "SINGLE_SUB"
		}

		FEATURE_INCLUDED = ["CASE_DUNS", "CASE_NAME", "CASE_SECOND_NAME", 
		                    "CASE_COUNTRY_NAME", "CASE_STATE_NAME", "CASE_CITY", 
		                    "GLOBAL_STATUS_CODE", "SUBSIDIARY_CODE", "GLOBAL_HIERARCHY_CODE",
		                    "SALES_US", "EMPLOYEES_HERE", "EMPLOYEES_TOTAL",
		                    "PARENT_DUNS", "GLOBAL_DUNS"]

		FEATURE_RENAME = {
		    "CASE_DUNS": "id",
		    "CASE_NAME": "name",
		    "CASE_SECOND_NAME": "subName",
		    "CASE_COUNTRY_NAME": "country",
		    "CASE_STATE_NAME": "state",
		    "CASE_CITY": "city",
		    "GLOBAL_STATUS_CODE": "status",
		    "SUBSIDIARY_CODE": "type",
		    "GLOBAL_HIERARCHY_CODE": "level",
		    "SALES_US": "value",
		    "EMPLOYEES_HERE": "size",
		    "EMPLOYEES_TOTAL": "sizeHere"
		}



	def get_entity_dict(self, df, feature_included):
	    global_ultimates = set()
	    entity_dict = {}
	    code_combination = set()
	    for _, row in df.iterrows():
	        cur_id = row["CASE_DUNS"]
	        entity_dict[cur_id] = {}
	        for feature in feature_included:
	            entity_dict[cur_id][feature] = row[feature]
	        code_combination.add((row["GLOBAL_STATUS_CODE"], row["SUBSIDIARY_CODE"]))
	        global_ultimates.add(row["GLOBAL_DUNS"])
	#     print(code_combination)
	    return global_ultimates, entity_dict
	 
	def get_parental_hierarchy(self, df, ignore_branches=True, prev_to_now={}, verbose=True):
	    entity_set = set(df["CASE_DUNS"].unique())
	    family_dict = defaultdict(lambda:{"parent": "", "children": set()})
	    no_parent_set = set()
	    root = []
	    branches_cnt = 0
	    
	    for _, row in df.iterrows():
	        cur_entity = row["CASE_DUNS"]
	        cur_parent = row["PARENT_DUNS"]
	        cur_domestic = row["DOMESTIC_DUNS"]
	        
	        # ignore braches
	        if row["GLOBAL_STATUS_CODE"] == "2" and row["SUBSIDIARY_CODE"] == "0":
	            branches_cnt += 1
	            if ignore_branches:
	                continue

	        if (cur_parent == cur_entity):
	            if verbose:
	                print("[LOG] Root found:", entity_dict[cur_entity]["CASE_NAME"], ", ID =", cur_entity)
	            root.append(cur_entity)
	            family_dict[cur_entity]["parent"] = "ROOT"
	        elif cur_parent not in entity_set:
	            if cur_parent in prev_to_now:
	                if verbose:
	                    print("[LOG] in prev_to_now")
	                cur_parent = prev_to_now[cur_parent]
	                family_dict[cur_entity]["parent"] = cur_parent
	                family_dict[cur_parent]["children"].add(cur_entity)
	            else:
	                if verbose:
	                    print("[WARNING]", entity_dict[cur_entity]["CASE_NAME"], 
	                          "'s parent (", cur_parent, ") is not in the database.")
	                if cur_domestic in entity_set:
	                    if cur_domestic != cur_entity:
	                        if verbose:
	                            print("          Domestic in the database:", 
	                                  entity_dict[cur_domestic]["CASE_NAME"], "!!!")
	                    else:
	                        if verbose:
	                            print("          Domestic in the database, but it is the entity itself.")
	                no_parent_set.add(cur_entity)
	                family_dict[cur_entity]["parent"] = cur_parent
	        else:
	            family_dict[cur_entity]["parent"] = cur_parent
	            family_dict[cur_parent]["children"].add(cur_entity)
	        
	    for cur_id, cur_family in family_dict.items():
	        family_dict[cur_id]["children"] = list(cur_family["children"])
	    
	    return root, family_dict, no_parent_set, branches_cnt

	def traverse_tree(self, family_dict, node, entity_in_tree):
	    for child in family_dict[node]["children"]:
	        traverse_tree(family_dict, child, entity_in_tree)
	    entity_in_tree.add(node)
	    return

	def extend_json_tree(self, tree_dict, entity_dict, node, feature_included, feature_rename):
	    json_tree = {}
	    for feature in feature_included:
	        new_feature_name = feature
	        if feature in feature_rename:
	            new_feature_name = feature_rename[feature]
	        json_tree[new_feature_name] = entity_dict[node][feature].title()
	    if len(tree_dict[node]["children"]) != 0:
	        json_tree["children"] = []
	        for entity in tree_dict[node]["children"]:
	            json_tree["children"].append(extend_json_tree(tree_dict, entity_dict, entity, feature_included, feature_rename))
	    return json_tree

	def look_for_entity(self, root, entity_dun, result):
	    if root["CASE_DUNS"] == entity_dun:
	        result.append(root)
	    if "children" not in root:
	        return
	    for child in root["children"]:
	        look_for_entity(child, entity_dun, result)
