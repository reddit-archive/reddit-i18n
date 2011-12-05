# The contents of this file are subject to the Common Public Attribution
# License Version 1.0. (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://code.reddit.com/LICENSE. The License is based on the Mozilla Public
# License Version 1.1, but Sections 14 and 15 have been added to cover use of
# software over a computer network and provide for limited attribution for the
# Original Developer. In addition, Exhibit A has been modified to be consistent
# with Exhibit B.
# 
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for
# the specific language governing rights and limitations under the License.
# 
# The Original Code is Reddit.
# 
# The Original Developer is the Initial Developer.  The Initial Developer of the
# Original Code is CondeNet, Inc.
# 
# All portions of the code written by CondeNet are Copyright (c) 2006-2009
# CondeNet, Inc. All Rights Reserved.
################################################################################

PO_FILES = $(wildcard reddit_i18n/*/LC_MESSAGES/r2.po)
MO_FILES = $(PO_FILES:.po=.mo)
ZO_FILES = $(PO_FILES:.po=.zo)
DATA_FILES = $(PO_FILES:.po=.data)

all: $(DATA_FILES) $(MO_FILES)

$(DATA_FILES): reddit_i18n/%/LC_MESSAGES/r2.data: reddit_i18n/%/LC_MESSAGES/r2.mo
	python gendata.py $@

$(MO_FILES): %.mo : %.po
	msgfmt $< -o $@

$(ZO_FILES): %.zo : %.po
	@echo -n "Updating $<..."
	@msgmerge -UN $< reddit_i18n/r2.pot 2>/dev/null && echo "done"

update: $(ZO_FILES)

clean:
	rm -f $(MO_FILES) $(DATA_FILES)

.PHONY: all clean update $(ZO_FILES)
