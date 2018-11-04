import pandas as pd
import numpy as np
from collections import defaultdict
from pprint import pprint

class EntityModel():


	def __init__(self, verbose=True):
		self.HIERARCHY_DICT = {
			('1','0'): "G-ULTIMATE",
			('1','3'): "SUBSIDIARY",
			('2','0'): "BRANCH",
			('0','3'): "SINGLE_SUB"
		}
		self.FEATURE_INCLUDED = [
			"CASE_DUNS", "CASE_NAME", "CASE_SECOND_NAME", 
			"CASE_COUNTRY_NAME", "CASE_STATE_NAME", "CASE_CITY", 
			"GLOBAL_STATUS_CODE", "SUBSIDIARY_CODE", "GLOBAL_HIERARCHY_CODE",
			"SALES_US", "EMPLOYEES_HERE", "EMPLOYEES_TOTAL",
			"PARENT_DUNS", "DOMESTIC_DUNS", "GLOBAL_DUNS"
		]
		self.FEATURE_RENAME = {
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
		self.verbose = verbose


	def upload(self, file):
		company_df = pd.read_csv(file, dtype=str)
		company_df.fillna("", inplace=True)
		self.global_ultimates, self.roots, self.entity_dict = self._get_entity_dict(company_df)
		self.prev_to_now_dict = self._get_prev_to_now_dict(company_df)


	def _get_prev_to_now_dict(self, company_df):
		prev_to_now = {}
		for _, row in company_df.iterrows():
			cur_id = row["CASE_DUNS"]
			prev_id = row["PREVIOUS_DUNS"]
			if prev_id != "":
				prev_to_now[prev_id] = cur_id
		return prev_to_now


	def _get_entity_dict(self, company_df):
		'''
		Extract info dict from the pandas dataframe.
		'''
		global_ultimates = set()
		roots = set()
		entity_dict = {}
		for _, row in company_df.iterrows():
			cur_id = row["CASE_DUNS"]
			entity_dict[cur_id] = {}
			for feature in self.FEATURE_INCLUDED:
				entity_dict[cur_id][feature] = row[feature]
			global_ultimates.add(row["GLOBAL_DUNS"])
			if row["CASE_DUNS"] == row["PARENT_DUNS"]:
				roots.add(row["CASE_DUNS"])
		return global_ultimates, list(roots), entity_dict
	 

	def _get_parental_hierarchy(self, ignore_branches=True):
		family_dict = defaultdict(lambda:{"parent": "", "children": set()})
		no_parent_set = set()
		branches_cnt = 0
		
		for key in self.entity_dict:
			row = self.entity_dict[key]

			cur_entity = row["CASE_DUNS"]
			cur_parent = row["PARENT_DUNS"]
			cur_domestic = row["DOMESTIC_DUNS"]
			
			# check and count branches
			if row["GLOBAL_STATUS_CODE"] == "2" and row["SUBSIDIARY_CODE"] == "0":
				branches_cnt += 1
				# ignore braches
				if ignore_branches:
					continue

			# be definition, root
			if (cur_parent == cur_entity):
				if self.verbose:
					print("[LOG] Root found:", self.entity_dict[cur_entity]["CASE_NAME"], ", ID =", cur_entity)
				family_dict[cur_entity]["parent"] = "ROOT"
			# parent not in dataset
			elif cur_parent not in self.entity_dict:
				# check if the previous duns of parent in dataset
				if cur_parent in self.prev_to_now_dict and self.prev_to_now_dict[cur_parent] in self.entity_dict:
					if self.verbose:
						print("[LOG] in prev_to_now")
					cur_parent = self.prev_to_now_dict[cur_parent]
					family_dict[cur_entity]["parent"] = cur_parent
					family_dict[cur_parent]["children"].add(cur_entity)
				# cannot find parent. try domestic parent. **TODO** use domestic as parent
				else:
					if self.verbose:
						print("[WARNING]", self.entity_dict[cur_entity]["CASE_NAME"], 
							  "'s parent (", cur_parent, ") is not in the database.")
					# check domestic as parent
					if cur_domestic in self.entity_dict:
						if cur_domestic != cur_entity:
							if self.verbose:
								print("Domestic in the database:", 
									  self.entity_dict[cur_domestic]["CASE_NAME"])
						else:
							if self.verbose:
								print("Domestic in the database, but it is the entity itself")
					# currently, no matter whether domestic can be used as parent or not, label this node as "parent-not-in-dataset entity"
					no_parent_set.add(cur_entity)
					family_dict[cur_entity]["parent"] = cur_parent
			# normal entity. update the entity's parent info and the entity's parent's children info
			else:
				family_dict[cur_entity]["parent"] = cur_parent
				family_dict[cur_parent]["children"].add(cur_entity)
			
		for cur_id, cur_family in family_dict.items():
			family_dict[cur_id]["children"] = list(cur_family["children"])
		
		return family_dict, no_parent_set, branches_cnt


	def _traverse_tree(self, family_dict, node, entity_in_tree):
		for child in family_dict[node]["children"]:
			self._traverse_tree(family_dict, child, entity_in_tree)
		entity_in_tree.add(node)
		return


	def _extend_json_tree(self, tree_dict, node):
		json_tree = {}
		for feature in self.FEATURE_INCLUDED:
			new_feature_name = feature
			if feature in self.FEATURE_RENAME:
				new_feature_name = self.FEATURE_RENAME[feature]
			json_tree[new_feature_name] = self.entity_dict[node][feature].title()
		if len(tree_dict[node]["children"]) != 0:
			json_tree["children"] = []
			for entity in tree_dict[node]["children"]:
				json_tree["children"].append(self._extend_json_tree(tree_dict, entity))
		return json_tree


	def _look_for_entity(self, root, entity_dun, result):
		if root["CASE_DUNS"] == entity_dun:
			result.append(root)
		if "children" not in root:
			return
		for child in root["children"]:
			look_for_entity(child, entity_dun, result)


	def stats_parent_not_in_dataset_entities(self, family_dict, no_parent_set):
		no_parent_tree_size = []
		no_parent_info = []

		for entity in no_parent_set:
			tmp = set()
			self._traverse_tree(family_dict, entity, tmp)
			no_parent_info.append((
				self.entity_dict[entity]["case_name".upper()].lower(), 
				self.entity_dict[entity]["global_status_code".upper()], 
				self.entity_dict[entity]["subsidiary_code".upper()], 
				self.entity_dict[entity]["global_hierarchy_code".upper()],
				self.HIERARCHY_DICT[(self.entity_dict[entity]["GLOBAL_STATUS_CODE"], self.entity_dict[entity]["SUBSIDIARY_CODE"])],
				str(len(tmp))
			))
			no_parent_tree_size.append(len(tmp))

		missing_parents = set()
		for index, tmp_root in enumerate(no_parent_set):
			missing_parents.add(self.entity_dict[tmp_root]["PARENT_DUNS"])
			
		if self.verbose:
			print("{:55s} | {:6s} | {:6s} | {:6s} | {:10s} | {}".format(
				"ENTITY_NAME", "STATUS", "SUBSID", "HIERAC", "TYPE", "CHILDREN_NUM"
			))

			for info in sorted(no_parent_info, key=lambda row:row[1]):
				print("{:55s} | {:6s} | {:6s} | {:6s} | {:10s} | {:4s}".format(
					info[0], info[1], info[2], info[3], info[4], info[5] 
				))

		return no_parent_tree_size, missing_parents


	def stats_roots(self, family_dict):
		tree_size = []
		for tmp_root in self.roots:
			entity_in_tree = set()
			self._traverse_tree(family_dict, tmp_root, entity_in_tree)
			tree_size.append(len(entity_in_tree))
		return tree_size


	def get_json_tree(self, root_type="most", ignore_branches=False):
		family_dict, no_parent_set, branches_cnt = \
			self._get_parental_hierarchy(ignore_branches=ignore_branches)
		tree_size = self.stats_roots(family_dict)
		if root_type == "most":
			root = self.roots[np.argmax(tree_size)]
		else:
			root = self.roots[0]
		json_tree = self._extend_json_tree(family_dict, root)
		return json_tree


	def get_data_stats(self, ignore_branches=False):
		family_dict, no_parent_set, branches_cnt = \
			self._get_parental_hierarchy(ignore_branches=ignore_branches)
		tree_size = self.stats_roots(family_dict)
		no_parent_tree_size, missing_parents = self.stats_parent_not_in_dataset_entities(family_dict, no_parent_set)

		print("# of All Entity:", len(self.entity_dict), "| # of Non-Branch Entity:", len(self.entity_dict) - branches_cnt)
		print("Root Entity (Parent's Duns = Self's Duns):", len(self.roots))
		print("Global Ultimates:", len(self.global_ultimates))
		print("In-Tree Entity (Ultimately reports to one of Root Entity):", np.sum(tree_size))
		print("Parent-Not-In-Dataset Entity:", len(no_parent_set), "(Missing Parents: " + str(len(missing_parents)) + ")")
		print("Out-Tree Entity (Ultimately reports to one of the Missing Parents):", np.sum(no_parent_tree_size))


if __name__ == '__main__':
	company_set = ['United_Technologies', 'Ingersoll_Rand', 'Eaton', 'Daikin', 'Captive_Aire']
	company_name = "Eaton"
	company_file = open("../dataset/ori_data/" + company_name + ".csv", "r")
	entity_model = EntityModel(verbose=False)
	entity_model.upload(company_file)
	entity_model.get_data_stats(ignore_branches=False)

