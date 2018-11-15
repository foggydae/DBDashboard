import pandas as pd
import numpy as np
from collections import defaultdict
from geopy.geocoders import DataBC
from pprint import pprint


class EntityModel():

    def __init__(self, verbose=True):
        self.HIERARCHY_DICT = {
            ('1', '0'): "root",
            ('1', '3'): "subsidiary",
            ('2', '0'): "branch",
            ('0', '3'): "subsidiary"
        }
        self.FEATURE_INCLUDED = [
            "CASE_DUNS", "CASE_NAME", "CASE_SECOND_NAME",
            "CASE_ADDRESS1", "CASE_COUNTRY_NAME", "CASE_STATE_NAME", "CASE_CITY",
            "GLOBAL_STATUS_CODE", "SUBSIDIARY_CODE", "GLOBAL_HIERARCHY_CODE",
            "SIC1", "SIC2", "SIC3", "SIC4", "SIC5", "SIC6",
            "SALES_US", "EMPLOYEES_HERE", "EMPLOYEES_TOTAL", "LOB",
            "PARENT_DUNS", "DOMESTIC_DUNS", "GLOBAL_DUNS",
            "REPORT_DATE", "latitude", "longitude"
        ]
        self.FEATURE_RENAME = {
            "CASE_DUNS": "id",
            "CASE_NAME": "name",
            "CASE_SECOND_NAME": "subName",
            "CASE_ADDRESS1": "address",
            "CASE_COUNTRY_NAME": "country",
            "CASE_STATE_NAME": "state",
            "CASE_CITY": "city",
            "GLOBAL_STATUS_CODE": "status",
            "SUBSIDIARY_CODE": "type",
            "GLOBAL_HIERARCHY_CODE": "level",
            "SALES_US": "revenue",
            "EMPLOYEES_HERE": "size",
            "EMPLOYEES_TOTAL": "sizeHere",
            "LOB": "LOB",
            "REPORT_DATE": "lastUpdate"
        }
        self.verbose = verbose

    def upload(self, file):
        company_df = pd.read_csv(file, dtype=str)
        company_df.fillna("", inplace=True)
        self.v_root = 'Virtual_Root'    # v_root will be the parent of all the company roots
        self.no_domestic_parent = 0
        self.max_level = 0
        self.global_ultimates, self.roots, self.entity_dict = self._get_entity_dict(company_df)
        self.virtual_entity_dict = self._create_virtual_entities()  # modified by _create_virtual_entities
        self.prev_to_now_dict = self._get_prev_to_now_dict(company_df)
        self.json_tree = self.get_json_tree()

        self.family_dict, self.no_parent_set, self.branches_cnt = \
            self._get_parental_hierarchy(ignore_branches=False)

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
        # geolocator = DataBC()
        for i, row in company_df.iterrows():
            cur_id = row["CASE_DUNS"]
            entity_dict[cur_id] = {}
            for feature in self.FEATURE_INCLUDED:
                entity_dict[cur_id][feature] = row[feature]
            entity_dict[cur_id]['Completeness'] = "{:.3f}".format(1 - sum(row == '')/len(row))
            entity_dict[cur_id]['SIC'] = ', '.join([row["SIC1"], row["SIC2"], row["SIC3"], row["SIC4"], row["SIC5"], row["SIC6"]])
            entity_dict[cur_id]['location'] = row['CASE_CITY'] + ", " + row['CASE_STATE_NAME'] + ", " + row['CASE_COUNTRY_NAME']

            entity_dict[cur_id]['size'] = row["EMPLOYEES_HERE"]
            entity_dict[cur_id]['revenue'] = row["SALES_US"]
            entity_dict[cur_id]['type'] = self.HIERARCHY_DICT[(row["GLOBAL_STATUS_CODE"], row["SUBSIDIARY_CODE"])]
            entity_dict[cur_id]['name'] = row["CASE_NAME"]
            entity_dict[cur_id]['lastUpdate'] = row["REPORT_DATE"]

            # infer gps information
            # address1 = row['CASE_ADDRESS1'] + ", " + row['CASE_CITY'] + ", " + row['CASE_STATE_NAME'] + ", " + row['CASE_COUNTRY_NAME']
            # address2 = row['CASE_CITY'] + ", " + row['CASE_STATE_NAME'] + ", " + row['CASE_COUNTRY_NAME']
            # address3 = row['CASE_CITY'] + ", " + row['CASE_STATE_NAME']
            # address4 = row['CASE_CITY'] + ", " + row['CASE_COUNTRY_NAME']
            # location = geolocator.geocode(address1) \
            #            or geolocator.geocode(address2) \
            #            or geolocator.geocode(address3) \
            #            or geolocator.geocode(address4)
            # if location:
            #     entity_dict[cur_id]['latitude'] = location.latitude
            #     entity_dict[cur_id]['longitude'] = location.longitude
            #     print(i, address1)
            #     print(i, location.latitude)
            # else:
            #     entity_dict[cur_id]['latitude'] = 'nan'
            #     entity_dict[cur_id]['longitude'] = 'nan'
            #     print(address1)
            #     print(location)

            global_ultimates.add(row["GLOBAL_DUNS"])
            if row["CASE_DUNS"] == row["PARENT_DUNS"]:
                roots.add(row["CASE_DUNS"])

            # track max level of the dataset in self.max_level
            self.max_level = max(self.max_level, int(row['GLOBAL_HIERARCHY_CODE']))

        self.FEATURE_INCLUDED.extend(['Completeness', 'SIC', 'location'])
        return global_ultimates, list(roots), entity_dict

    def _create_virtual_entities(self):
        virtual_entity_dict = {}
        # add an virtual root
        virtual_entity_dict['Virtual_Root'] = {}
        for feature in self.FEATURE_INCLUDED:
            virtual_entity_dict['Virtual_Root'][feature] = ''
        virtual_entity_dict['Virtual_Root']["CASE_DUNS"] = "Virtual_Root"
        virtual_entity_dict['Virtual_Root']["CASE_NAME"] = "Virtual_Root"
        virtual_entity_dict['Virtual_Root']["PARENT_DUNS"] = "Virtual_Root"

        # create virtual nodes
        for i in range(1, self.max_level):
            v_node = "Virtual_Node_Level_" + str(i)
            v_node_parent = "Virtual_Node_Level_" + str(i - 1) if i > 1 else "Virtual_Root"
            virtual_entity_dict[v_node] = {}
            for feature in self.FEATURE_INCLUDED:
                virtual_entity_dict[v_node][feature] = ''
            virtual_entity_dict[v_node]["CASE_DUNS"] = v_node
            virtual_entity_dict[v_node]["CASE_NAME"] = v_node
            virtual_entity_dict[v_node]["PARENT_DUNS"] = v_node_parent
        return virtual_entity_dict


    def _get_parental_hierarchy(self, ignore_branches=True):
        """

        :param ignore_branches:
        :return:
        family_dict: {DUNS_number: {'parent':'', 'children':[]}, ...}
        no_parent_set: set of children's DUNS
        branches_cnt: count of branches (int)
        """
        family_dict = defaultdict(lambda: {"parent": "", "children": set()})
        no_parent_set = set()
        branches_cnt = 0

        for i, key in enumerate(self.entity_dict):
            row = self.entity_dict[key]

            cur_entity = row["CASE_DUNS"]
            cur_parent = row["PARENT_DUNS"]
            cur_domestic = row["DOMESTIC_DUNS"]
            cur_level = int(row["GLOBAL_HIERARCHY_CODE"])

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
                # family_dict[cur_entity]["parent"] = "ROOT"
                family_dict[cur_entity]["parent"] = "Virtual_Root"
                family_dict["Virtual_Root"]["children"].add(cur_entity)
            # parent not in dataset
            elif cur_parent not in self.entity_dict:
                # check if the previous duns of parent in dataset
                if cur_parent in self.prev_to_now_dict and self.prev_to_now_dict[cur_parent] in self.entity_dict:
                    if self.verbose:
                        print("[LOG] in prev_to_now")
                    cur_parent = self.prev_to_now_dict[cur_parent]
                    family_dict[cur_entity]["parent"] = cur_parent
                    family_dict[cur_parent]["children"].add(cur_entity)
                # cannot find parent. try domestic parent. **Implemented** use domestic as parent
                else:
                    if self.verbose:
                        print("[WARNING]", self.entity_dict[cur_entity]["CASE_NAME"],
                              "'s parent (", cur_parent, ") is not in the database.")
                    # check domestic as parent
                    if cur_domestic in self.entity_dict and cur_domestic != cur_entity:
                        # if cur_domestic != cur_entity:
                        if self.verbose:
                            print("Domestic in the database:",
                                  self.entity_dict[cur_domestic]["CASE_NAME"])
                        # use domestic parent as parent
                        family_dict[cur_entity]["parent"] = cur_domestic
                        family_dict[cur_domestic]["children"].add(cur_entity)
                        # else:
                        #     if self.verbose:
                        #         print("Domestic in the database, but it is the entity itself")

                    # domestic parent not in dataset or domestic parent is itself
                    else:
                        self.no_domestic_parent += 1
                        if cur_parent not in self.virtual_entity_dict:
                            # create a virtual node as its parent
                            self.virtual_entity_dict[cur_parent] = {}
                            for feature in self.FEATURE_INCLUDED:
                                self.virtual_entity_dict[cur_parent][feature] = ''
                            self.virtual_entity_dict[cur_parent]["CASE_DUNS"] = cur_parent
                            self.virtual_entity_dict[cur_parent]["CASE_NAME"] = "Virtual Node: " + cur_parent
                            self.virtual_entity_dict[cur_parent]["PARENT_DUNS"] = \
                                "Virtual_Node_Level_" + str(cur_level - 1) if cur_level > 1 else "Virtual_Root"

                        # add parent relation with the virtual node
                        family_dict[cur_entity]["parent"] = cur_parent
                        family_dict[cur_parent]["children"].add(cur_entity)

                    # currently, no matter whether domestic can be used as parent or not, label this node as "parent-not-in-dataset entity"
                    no_parent_set.add(cur_entity)
                    family_dict[cur_entity]["parent"] = cur_parent
            # normal entity. update the entity's parent info and the entity's parent's children info
            else:
                family_dict[cur_entity]["parent"] = cur_parent
                family_dict[cur_parent]["children"].add(cur_entity)

        for i, key in enumerate(self.virtual_entity_dict):
            row = self.virtual_entity_dict[key]

            cur_entity = row["CASE_DUNS"]
            cur_parent = row["PARENT_DUNS"]

            if cur_entity == "Virtual_Root":
                continue

            # link virtual nodes to it parents
            family_dict[cur_entity]["parent"] = cur_parent
            family_dict[cur_parent]["children"].add(cur_entity)

        for cur_id, cur_family in family_dict.items():
            family_dict[cur_id]["children"] = list(cur_family["children"])  # change from set to list

        return family_dict, no_parent_set, branches_cnt

    def _traverse_tree(self, family_dict, node, entity_in_tree):
        for child in family_dict[node]["children"]:
            self._traverse_tree(family_dict, child, entity_in_tree)
        entity_in_tree.add(node)
        return

    def _extend_json_tree(self, family_dict, node):
        json_tree = {}
        for feature in self.FEATURE_INCLUDED:
            new_feature_name = feature
            if feature in self.FEATURE_RENAME:
                new_feature_name = self.FEATURE_RENAME[feature]
            try:
                json_tree[new_feature_name] = self.entity_dict[node][feature].title()
            except KeyError as e:
                json_tree[new_feature_name] = self.virtual_entity_dict[node][feature].title()
        if len(family_dict[node]["children"]) != 0:
            json_tree["children"] = []
            for entity in family_dict[node]["children"]:
                json_tree["children"].append(self._extend_json_tree(family_dict, entity))
        return json_tree

    def _look_for_entity(self, root, entity_dun, result):
        if root["CASE_DUNS"] == entity_dun:
            result.append(root)
        if "children" not in root:
            return
        for child in root["children"]:
            self._look_for_entity(child, entity_dun, result)

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
                self.HIERARCHY_DICT[
                    (self.entity_dict[entity]["GLOBAL_STATUS_CODE"], self.entity_dict[entity]["SUBSIDIARY_CODE"])],
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

            for info in sorted(no_parent_info, key=lambda row: row[1]):
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

    def get_json_tree(self, ignore_branches=False):
        family_dict, no_parent_set, branches_cnt = \
            self._get_parental_hierarchy(ignore_branches=ignore_branches)
        # tree_size = self.stats_roots(family_dict)
        # if root_type == "most":
        #     root = self.roots[np.argmax(tree_size)]
        # else:
        #     root = self.roots[0]

        json_tree = self._extend_json_tree(family_dict, self.v_root)
        return json_tree

    def get_data_stats(self, ignore_branches=False):
        family_dict, no_parent_set, branches_cnt = \
            self._get_parental_hierarchy(ignore_branches=ignore_branches)
        tree_size = self.stats_roots(family_dict)
        no_parent_tree_size, missing_parents = self.stats_parent_not_in_dataset_entities(family_dict, no_parent_set)

        print("# of All Entity:", len(self.entity_dict), "| # of Non-Branch Entity:",
              len(self.entity_dict) - branches_cnt)
        print("Root Entity (Parent's Duns = Self's Duns):", len(self.roots))
        print("Global Ultimates:", len(self.global_ultimates))
        print("In-Tree Entity (Ultimately reports to one of Root Entity):", np.sum(tree_size))
        print("Parent-Not-In-Dataset Entity:", len(no_parent_set),
              "(Missing Parents: " + str(len(missing_parents)) + ")")
        print("Out-Tree Entity (Ultimately reports to one of the Missing Parents):", np.sum(no_parent_tree_size))


    def get_gps(self, case_duns='ALL'):
        """
        if case_duns is specified, return its gps and its children's and grand-children's gps
        otherwise return all gps in the file
    
        :return:
        {case_duns: {"latitude": latitude, "longitude": longitude, “size”: employee_num, "revenue": revenue, ...}}
        """
    
        locations_dict = {}
        if case_duns == 'ALL':
            return self.entity_dict
        else:
            entities = set()
            self._traverse_tree(self.family_dict, node=case_duns, entity_in_tree=entities)
            return {entity: self.entity_dict[entity] for entity in entities}


if __name__ == '__main__':
    company_set = ['United_Technologies', 'Ingersoll_Rand', 'Eaton', 'Daikin', 'Captive_Aire']
    company_name = "Ingersoll_Rand"
    company_file = open("../dataset/ori_data/" + company_name + ".csv", "r")
    entity_model = EntityModel(verbose=False)
    entity_model.upload(company_file)
    entity_model.get_data_stats(ignore_branches=False)
    print('# of no Domestic Parent:', entity_model.no_domestic_parent)
