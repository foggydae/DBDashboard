import pandas as pd
import numpy as np
from collections import defaultdict
from geopy import distance
from geopy.geocoders import DataBC
from pprint import pprint
from numpy.linalg import norm
from numpy import dot

import json
import math


class EntityModel():

    def __init__(self, verbose=True):
        self.HIERARCHY_DICT = {
            ('1', '0'): "root",
            ('1', '3'): "subsidiary",
            ('2', '0'): "branch",
            ('0', '3'): "subsidiary"
        }
        self.verbose = verbose
        self.v_root = 'Virtual_Root'  # v_root will be the parent of all the company roots

    def upload(self, file):
        """
        upload DB csv file; initialize variables associated with the file
        :param file: a csv file with the same format as that provided.
        """

        self.company_df = pd.read_csv(file, dtype=str)
        self.company_df.fillna("", inplace=True)
        print("shape:", self.company_df.shape)
        size_quantiles = self.company_df['EMPLOYEES_HERE'].astype(int).quantile(np.linspace(0.1,1,10)).values

        def _get_quantile(employee_num):
            return np.argmax((size_quantiles - int(employee_num)) > 0) + 1

        max_employees_here = self.company_df['EMPLOYEES_HERE'].astype(float).max()
        # self.company_df['size'] = self.company_df['EMPLOYEES_HERE'].apply(lambda x:(float(x)/max_employees_here)*9+5) # scale number of employee to size 1-10
        self.company_df['size'] = self.company_df['EMPLOYEES_HERE'].apply(lambda x:math.sqrt(math.sqrt(float(x))) * 1.8 + 3) # scale number of employee to size

        with open("../DBDashboard/Utils/sic_dict.json", "r") as f:
            sic_dict = json.load(f)

        self.max_level = 0
        self.global_ultimates, self.roots, self.feature_included, self.entity_dict = \
            self._get_entity_dict(self.company_df, sic_dict)
        self.virtual_entity_dict = self._create_virtual_entities()
        self.prev_to_now_dict = self._get_prev_to_now_dict(self.company_df)

        self.no_domestic_parent = 0
        self.family_dict, self.no_parent_set, self.branches_cnt = \
            self._get_parental_hierarchy()

    def _get_prev_to_now_dict(self, company_df):
        """
        Build a previous DUNS number to current DUNS number dictionary
        :param company_df
        """
        prev_to_now = {}
        for _, row in company_df.iterrows():
            cur_id = row["CASE_DUNS"]
            prev_id = row["PREVIOUS_DUNS"]
            if prev_id != "":
                prev_to_now[prev_id] = cur_id
        return prev_to_now

    def _get_entity_dict(self, company_df, sic_dict):
        '''
        Extract info dict from the pandas dataframe.
        Strore all entity information in entity_dict, whose key is DUNS number.
        '''
        global_ultimates = {}
        roots = set()
        feature_included = {'id', 'name', 'size', 'sizeTotal', 'empNum', 'revenue', 'lastUpdate', 'address', 'LOB',
                            'latitude', 'longitude', 'type', 'Completeness', 'SIC', 'SIC_ori', 'location', 'level', 'domestic',
                            'parent', }
        entity_dict = {}
        # For each row in the excel file, add into entity_dict
        for i, row in company_df.iterrows():
            cur_id = row["CASE_DUNS"]
            entity_dict[cur_id] = {}

            entity_dict[cur_id]['id'] = cur_id
            entity_dict[cur_id]['name'] = row["CASE_NAME"]
            entity_dict[cur_id]['size'] = row["size"]
            entity_dict[cur_id]['empNum'] = row["EMPLOYEES_HERE"]
            entity_dict[cur_id]['sizeTotal'] = row["EMPLOYEES_TOTAL"]
            entity_dict[cur_id]['lastUpdate'] = row["REPORT_DATE"]
            entity_dict[cur_id]['revenue'] = row["SALES_US"]
            entity_dict[cur_id]['address'] = row["CASE_ADDRESS1"]
            entity_dict[cur_id]['LOB'] = row["LOB"]
            entity_dict[cur_id]['level'] = row['GLOBAL_HIERARCHY_CODE']
            # check if gps info is included in the dataset
            if 'latitude' and 'longitude' in row.keys():
                entity_dict[cur_id]['latitude'] = row["latitude"]
                entity_dict[cur_id]['longitude'] = row["longitude"]
                feature_included.add('latitude')
                feature_included.add('longitude')
            entity_dict[cur_id]['domestic'] = row["DOMESTIC_DUNS"]
            entity_dict[cur_id]['parent'] = row["PARENT_DUNS"]
            entity_dict[cur_id]['type'] = self.HIERARCHY_DICT[(row["GLOBAL_STATUS_CODE"], row["SUBSIDIARY_CODE"])]

            entity_dict[cur_id]['Completeness'] = "{:.3f}".format(1 - sum(row == '') / len(row))
            entity_dict[cur_id]['SIC'] = '</br>'.join(
                [row["SIC" + str(i)] + "-" + sic_dict[row["SIC" + str(i)][:4]].title() for i in range(1, 7) if row["SIC" + str(i)] != ""])
            entity_dict[cur_id]['SIC_ori'] = ', '.join(
                [row["SIC" + str(i)] for i in range(1, 7) if row["SIC" + str(i)] != ""])
            entity_dict[cur_id]['location'] = row['CASE_CITY'] + ", " + row['CASE_STATE_NAME'] + ", " + row['CASE_COUNTRY_NAME']

            global_ultimates[row["GLOBAL_DUNS"]] = {
                "name": row["GLOBAL_NAME"], 
                "location": row['GLOBAL_CITY'] + ", " + row['GLOBAL_STATE'] + ", " + row['GLOBAL_COUNTRY_NAME'],
                "address": row['GLOBAL_ADDRESS']
            }
            if row["CASE_DUNS"] == row["PARENT_DUNS"]:
                roots.add(row["CASE_DUNS"])

            # track max level of the dataset in self.max_level
            self.max_level = max(self.max_level, int(row['GLOBAL_HIERARCHY_CODE']))

        return global_ultimates, list(roots), list(feature_included), entity_dict

    def _create_virtual_entities(self):
        """
        For each level create an virtual node. All the virtual will be saved in virtual_entity_dict
        :return: virtual_entity_dict
        """
        virtual_entity_dict = {}
        # add an virtual root
        virtual_entity_dict[self.v_root] = {}
        for feature in self.feature_included:
            virtual_entity_dict[self.v_root][feature] = 'virtual'
        virtual_entity_dict[self.v_root]["id"] = self.v_root
        virtual_entity_dict[self.v_root]["name"] = self.v_root
        virtual_entity_dict[self.v_root]["parent"] = self.v_root
        virtual_entity_dict[self.v_root]["type"] = "virtual_root"
        virtual_entity_dict[self.v_root]["level"] = "00"
        virtual_entity_dict[self.v_root]["size"] = 1
        virtual_entity_dict[self.v_root]["revenue"] = 0

        # create virtual nodes
        for i in range(1, self.max_level):
            v_node = "Virtual_Node_Level_" + str(i)
            v_node_parent = "Virtual_Node_Level_" + str(i - 1) if i > 1 else self.v_root
            virtual_entity_dict[v_node] = {}
            for feature in self.feature_included:
                virtual_entity_dict[v_node][feature] = 'virtual'
            virtual_entity_dict[v_node]["id"] = v_node
            virtual_entity_dict[v_node]["name"] = v_node
            virtual_entity_dict[v_node]["parent"] = v_node_parent
            virtual_entity_dict[v_node]["type"] = "virtual"
            virtual_entity_dict[v_node]["level"] = str(i).zfill(2)
            virtual_entity_dict[v_node]["size"] = 1
            virtual_entity_dict[v_node]["revenue"] = 0
        return virtual_entity_dict

    def _get_parental_hierarchy(self, ignore_branches=False):
        """
        :param ignore_branches
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

            cur_entity = row["id"]
            cur_parent = row["parent"]
            cur_domestic = row["domestic"]
            cur_level = int(row["level"])

            # check and count branches
            if row["type"] == "branch":
                branches_cnt += 1
                # ignore braches
                if ignore_branches:
                    continue

            # be definition, root
            if (cur_parent == cur_entity):
                if self.verbose:
                    print("[LOG] Root found:", self.entity_dict[cur_entity]["name"], ", ID =", cur_entity)
                # family_dict[cur_entity]["parent"] = "ROOT"
                family_dict[cur_entity]["parent"] = self.v_root
                family_dict[self.v_root]["children"].add(cur_entity)
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
                        print("[WARNING]", self.entity_dict[cur_entity]["name"],
                              "'s parent (", cur_parent, ") is not in the database.")
                    # check domestic as parent
                    if cur_domestic in self.entity_dict and cur_domestic != cur_entity:
                        # if cur_domestic != cur_entity:
                        if self.verbose:
                            print("Domestic in the database:",
                                  self.entity_dict[cur_domestic]["name"])
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
                            for feature in self.feature_included:
                                self.virtual_entity_dict[cur_parent][feature] = 'virtual'
                            self.virtual_entity_dict[cur_parent]["id"] = cur_parent
                            self.virtual_entity_dict[cur_parent]["name"] = "Virtual Node: " + cur_parent
                            self.virtual_entity_dict[cur_parent]["parent"] = \
                                "Virtual_Node_Level_" + str(cur_level - 1) if cur_level > 1 else self.v_root
                            self.virtual_entity_dict[cur_parent]["type"] = "virtual"
                            self.virtual_entity_dict[cur_parent]["level"] = row["level"]
                            self.virtual_entity_dict[cur_parent]["size"] = 1
                            self.virtual_entity_dict[cur_parent]["revenue"] = 0

                        # add parent relation with the virtual node
                        family_dict[cur_entity]["parent"] = cur_parent
                        family_dict[cur_parent]["children"].add(cur_entity)
                        # currently, no matter whether domestic can be used as parent or not, label this node as "parent-not-in-dataset entity"
                        no_parent_set.add(cur_entity)

            # normal entity. update the entity's parent info and the entity's parent's children info
            else:
                family_dict[cur_entity]["parent"] = cur_parent
                family_dict[cur_parent]["children"].add(cur_entity)

        for i, key in enumerate(self.virtual_entity_dict):
            row = self.virtual_entity_dict[key]

            cur_entity = row["id"]
            cur_parent = row["parent"]

            if cur_entity == self.v_root:
                continue

            # link virtual nodes to it parents
            family_dict[cur_entity]["parent"] = cur_parent
            family_dict[cur_parent]["children"].add(cur_entity)

        for cur_id, cur_family in family_dict.items():
            family_dict[cur_id]["children"] = list(cur_family["children"])  # change from set to list

        return family_dict, no_parent_set, branches_cnt

    def _traverse_tree(self, family_dict, node, entity_in_tree):
        """
        Give a node, traverse all its children in the tree. Store all the nodes in a passed set
        :param family_dict:
        :param node:
        :param entity_in_tree:
        :return:
        """
        for child in family_dict[node]["children"]:
            self._traverse_tree(family_dict, child, entity_in_tree)
        entity_in_tree.add(node)
        return

    def _extend_json_tree(self, family_dict, node):
        json_tree = {}
        for feature in self.feature_included:
            try:
                json_tree[feature] = self.entity_dict[node][feature]
            except KeyError as e:
                json_tree[feature] = self.virtual_entity_dict[node][feature]
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

    def _highlight_rules(self, duns, key):
        # parent-not-in-dataset entity, highlight the parent duns
        if duns in self.no_parent_set and key == "parent":
            return "yes"
        # global ultimate that does not show up in the dataset
        if duns in self.global_ultimates and duns not in self.roots:
            return "yes"
        # global ultimate that does not show up in the dataset
        if self.entity_dict[duns][key] in self.global_ultimates and self.entity_dict[duns][key] not in self.roots:
            return "yes"
        # others
        return "no"

    def _count_pnids(self):
        """
        calculate the missing_parent nodes of the dataset
        :return:
        """
        no_parent_tree_size = []
        no_parent_info = []

        for entity in self.no_parent_set:
            tmp = set()
            self._traverse_tree(self.family_dict, entity, tmp)
            no_parent_info.append((
                self.entity_dict[entity]["name"],
                self.entity_dict[entity]["level"],
                self.entity_dict[entity]["type"],
                str(len(tmp))
            ))
            no_parent_tree_size.append(len(tmp))

        missing_parents = set()
        for index, tmp_root in enumerate(self.no_parent_set):
            missing_parents.add(self.entity_dict[tmp_root]["parent"])

        if self.verbose:
            print("{:55s} | {:6s} | {:10s} | {}".format(
                "ENTITY_NAME", "HIERAC", "TYPE", "CHILDREN_NUM"
            ))

            for info in sorted(no_parent_info, key=lambda row: row[1]):
                print("{:55s} | {:6s} | {:10s} | {:4s}".format(
                    info[0], info[1], info[2], info[3]
                ))

        return no_parent_tree_size, missing_parents

    def _count_roots(self):
        """
        calculate the number of roots in the dataset.
        """
        tree_size = []
        for tmp_root in self.roots:
            entity_in_tree = set()
            self._traverse_tree(self.family_dict, tmp_root, entity_in_tree)
            tree_size.append(len(entity_in_tree))
        return tree_size

    def count_subs_branches(self, node_duns):
        """
        count the number of children under one node. (used in Phase II recommendation)
        """
        sub_tree_set = set()
        self._traverse_tree(self.family_dict, node_duns, sub_tree_set)
        num_branches = 0
        for entity_duns in sub_tree_set:
            if self.entity_dict[entity_duns]["type"] == "branch":
                num_branches += 1
        return num_branches, len(sub_tree_set) - num_branches

    def get_json_tree(self, ignore_branches=False):
        if ignore_branches:
            family_dict, _, _ = \
                self._get_parental_hierarchy(ignore_branches=True)
        else:
            family_dict = self.family_dict

        json_tree = self._extend_json_tree(family_dict, self.v_root)
        return json_tree

    def get_data_stats(self, verbose=True):
        tree_size = self._count_roots()
        no_parent_tree_size, missing_parents = self._count_pnids()

        root_revenue = 0
        root_emp = 0
        for tmp_root in self.roots:
            root_revenue += int(self.entity_dict[tmp_root]["revenue"])
            root_emp += int(self.entity_dict[tmp_root]["sizeTotal"])

        missing_ultimates = set(self.global_ultimates.keys()) - set(self.roots)


        if verbose:
            print("# of All Entity:", len(self.entity_dict), "| # of Non-Branch Entity:",
                  len(self.entity_dict) - self.branches_cnt)
            print("Root Entity (Parent's Duns = Self's Duns):", len(self.roots))
            print("Global Ultimates:", len(self.global_ultimates))
            print("In-Tree Entity (Ultimately reports to one of Root Entity):", np.sum(tree_size))
            print("Parent-Not-In-Dataset Entity:", len(self.no_parent_set),
                  "(Missing Parents: " + str(len(missing_parents)) + ")")
            print("Out-Tree Entity (Ultimately reports to one of the Missing Parents):", np.sum(no_parent_tree_size))
            print("Max Hierarchy:", self.max_level)
            print("root total revenue:", root_revenue)
            print("root total employee:", root_emp)

        tree_count = {
            "total": len(self.entity_dict),
            "non_branch": len(self.entity_dict) - self.branches_cnt,
            "branch": self.branches_cnt,
            "root": len(self.roots),
            "in_tree": int(np.sum(tree_size)),
            "pnid": len(self.no_parent_set),
            "out_tree": int(np.sum(no_parent_tree_size)),
            "max_hierarchy": self.max_level,
            "global_ultimates": len(self.global_ultimates),
            "missing_ultimates": len(missing_ultimates),
            "root_revenue": root_revenue,
            "root_emp": root_emp
        }
        return tree_count


    def get_pnid_list(self):
        return [{key:{"value":self.entity_dict[duns][key],"status":self._highlight_rules(duns, key)} for key in self.entity_dict[duns] if key not in {"SIC", "size", "latitude", "longitude"}} 
                for duns in self.no_parent_set]


    def get_global_ultimates(self):
        return [{duns:{"value":self.global_ultimates[duns]["name"],"status":self._highlight_rules(duns, "name")} 
            for duns in self.global_ultimates}]


    def get_metadata(self):
        return [{key:{"value":self.entity_dict[duns][key],"status":self._highlight_rules(duns, key)} for key in self.entity_dict[duns] if key not in {"SIC", "size", "latitude", "longitude"}}
                for duns in self.entity_dict]


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


    def find_siblings(self, case_duns, digits=2, logic='OR', max_num=20):
        """

        :param case_duns: the DUNS number of currently selected entity
        :param digits: number of digits used to find siblings
        :param logic: chocie from 'AND', 'OR'.
               'AND': a siblings must have ALL the SIC codes that have the first several digits with the selected entity
               'OR' : a siblings have ANY SIC codes that have the first several digits with the selected entity
        :param max_num: the maximum number of siblings that will be
        :return:
        """
        if case_duns == "INIT":
            case_duns = self.roots[0];

        company_df = self.company_df
        entity = self.entity_dict[case_duns]
        lat1 = float(entity['latitude'])
        lon1 = float(entity['longitude'])

        def _compare_sics(row):
            """
            Combine 6 SIC code into one string.
            """
            sics = ''.join(sorted([row["SIC" + str(i)][:digits] for i in range(1, 7) if row["SIC" + str(i)] != ""]))
            return sics == combined_sics

        def _cal_dist(row):
            try:
                lat2, lon2 = float(row['latitude']), float(row['longitude'])
            except:
                lat2 = 0
                lon2 = 0
            return distance.distance((lat1, lon1), (lat2,lon2))
        sics = entity['SIC_ori'].split(sep=', ')
        if logic == 'OR':
            for sic in sics:
                if str(sic) != '':
                    siblings = company_df.loc[(company_df['SIC1'].apply(lambda x: x[:digits] == sic[:digits])) |
                                            (company_df['SIC2'].apply(lambda x: x[:digits] == sic[:digits])) |
                                            (company_df['SIC3'].apply(lambda x: x[:digits] == sic[:digits])) |
                                            (company_df['SIC4'].apply(lambda x: x[:digits] == sic[:digits])) |
                                            (company_df['SIC5'].apply(lambda x: x[:digits] == sic[:digits])) |
                                            (company_df['SIC6'].apply(lambda x: x[:digits] == sic[:digits]))
                                           ]
        else: # logic == 'AND'
            combined_sics = ''.join(sorted([sic[:digits] for sic in sics]))
            if str(combined_sics) != '':
                siblings = company_df.loc[(company_df.apply(_compare_sics, axis=1))]

        # sort result (by distance asc)
        siblings['distance'] = siblings.apply(_cal_dist, axis=1)
        nearest_siblings = siblings.sort_values('distance')[:max_num]

        siblings_list = [self.entity_dict[row["CASE_DUNS"]] for _, row in nearest_siblings.iterrows() if row["CASE_DUNS"] != case_duns]
        siblings_list = [self.entity_dict[case_duns]] + siblings_list

        return siblings_list

    def similarity_score(self, case_duns, weights, digits=2, logic='OR'):
        """
        calcualte the similarity score between one entity and its siblings. (used in Phase II recommendation)
        """
        def calc_cosine_similarity(row1, row2):
            norm1 = norm(row1)
            norm2 = norm(row2)
            if norm1 == 0 or norm2 == 0:
                return 0
            else:
                return np.inner(row1, row2) / (norm1 * norm2)

        # Set the required columns
        columns = ["id", "level", "revenue", "empNum", 'branches_count', 'subsidiaries_count', 'longitude', 'latitude']
        # pad weight for location
        weights.append(weights[-1])
        weights = np.array(weights) + 0.00001
        
        # prepare dataframe
        siblings = self.find_siblings(case_duns, digits, logic, max_num=100) # without the selected_case
        siblings_df = pd.DataFrame(siblings)
        siblings_df['branches_count'] = siblings_df["id"].apply(lambda x: self.count_subs_branches(x)[0])
        siblings_df['subsidiaries_count'] = siblings_df["id"].apply(lambda x: self.count_subs_branches(x)[1])
        siblings_df = siblings_df[columns]

        siblings_df['level'] = siblings_df['level'].astype(float)
        siblings_df['revenue'] = siblings_df['revenue'].astype(float)
        siblings_df['empNum'] = siblings_df['empNum'].astype(float)
        siblings_df['longitude'] = siblings_df['longitude'].astype(float)
        siblings_df['latitude'] = siblings_df['latitude'].astype(float)
        id_columns = siblings_df["id"]
        siblings_df.drop(columns=["id"], inplace=True)

        # normalize & weight
        normalized_df = (siblings_df - siblings_df.min()) / (siblings_df.max() - siblings_df.min())
        weighted_df = normalized_df * weights
        weighted_df["score"] = weighted_df.apply(lambda row:calc_cosine_similarity(list(row), list(weighted_df.iloc[0])), axis=1)
        weighted_df["id"] = id_columns

        weighted_df.sort_values(by="score", ascending=False, inplace=True)
        sorted_duns = list(weighted_df["id"])

        sorted_duns
        siblings_list = [self.entity_dict[duns_id] for duns_id in sorted_duns if duns_id != case_duns]
        return [self.entity_dict[case_duns]] + siblings_list

    def get_lob_list(self):
        return sorted(list(self.company_df["LOB"].unique()))


    def filter_word(self, keyword, dun_id):
        """
        :param keyword: keyword to search
        :param dun_id: DUNS number
        :return: boolean variable indicate if a keyword is in the record
        """
        if keyword in self.entity_dict[dun_id]["name"].lower():
            return True
        if keyword in self.entity_dict[dun_id]["location"].lower():
            return True
        if keyword in self.entity_dict[dun_id]["address"].lower():
            return True
        if keyword in self.entity_dict[dun_id]["id"].lower():
            return True
        return False

    def filter_lob(self, lob_set, dun_id):
        """
        filter entities based on keyword.
        """
        if len(lob_set) == 0 or self.entity_dict[dun_id]["LOB"] in lob_set:
            return True
        return False


    def filter_entity(self, keyword, lob):
        """
        filter entities based on keyword and line of business
        """
        keyword = keyword.lower()
        lob_set = set(lob)
        result = set([dun_id for dun_id in self.entity_dict if self.filter_word(keyword, dun_id) and self.filter_lob(lob_set, dun_id)])
        return list(set(self.entity_dict.keys()) - result)


# code for debugging 
if __name__ == '__main__':
    #company_set = ['United_Technologies', 'Ingersoll_Rand', 'Eaton', 'Daikin', 'Captive_Aire']
    company_name = "Eaton_gps"
    company_file = open("../dataset/ori_data/" + company_name + ".csv", "r")
    #entity_model = EntityModel(verbose=False)
    #entity_model.upload(company_file)
    # print(entity_model.count_subs_branches("00001368026"))
    # entity_model.get_data_stats(verbose=True)
    #company_name = "Eaton_gps"
    #company_file = open("~/Desktop/data/ori_data/" + company_name + ".csv", "r")
    entity_model = EntityModel(verbose=False)
    entity_model.upload(company_file)
    weights = [0.8, 0.05, 0.05, 0.03, 0.03, 0.04]
    pprint(entity_model.similarity_score('00129464363',weights))
    #print(entity_model.similarity_score('00129464363',weights, False))
