#
# Copyright 2018 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


import sys
import json
import re

def findNewCommit(oldCommitMap, newCommitMap):
    branch = ""
    commitId = ""

    # loop over new map branches
    for newBranch, newCommitId in newCommitMap.iteritems():
        # check if branch exists in old map
        if newBranch in oldCommitMap:
            oldCommitId = oldCommitMap[newBranch]
            # compare commit ids
            if newCommitId != oldCommitId:
                branch = newBranch
                commitId = newCommitId
                break
        else:
            # new branch, this triggered it
            branch = newBranch
            commitId = newCommitId
            break

    return branch, commitId

if server is None:
    print "No Bitbucket server provided."
    sys.exit(1)

request = HttpRequest(server, username, password)
context = "/rest/api/1.0/projects/%s/repos/%s" % (project, repository)
branches_path = "%s/%s?limit=1000" % (context, "branches")
response = request.get(branches_path, contentType = 'application/json')

if not response.isSuccessful():
    if response.status == 404 and triggerOnInitialPublish:
        print "Repository '%s:%s' not found in bitbucket. Ignoring." % (project, repository)

        if not triggerState:
            branch = commitId = triggerState = 'unknown'
    else:
        print "Failed to fetch branch information from Bitbucket server %s" % server['url']
        response.errorDump()
    sys.exit(1)
else:
    info = json.loads(response.response)

    # build a map of the commit ids for each branch
    newCommit = {}
    for branch in info["values"]:
        if branch["displayId"] not in excludeBranches.strip(" ").strip(",").split(","):
            branchid = branch["displayId"]
            lastcommit = branch["latestCommit"]
            newCommit[branchid] = lastcommit

    # trigger state is perisisted as json
    newTriggerState = json.dumps(newCommit)

    if triggerState != newTriggerState:
        if len(triggerState) == 0:
            oldCommit = {}
        else:
            oldCommit = json.loads(triggerState)

        branch, commitId = findNewCommit(oldCommit, newCommit)

        if not branchName or (branchName and branchName == branch ):
            triggerState = newTriggerState

            if retrieveMessage:
                # make http call to get commit
                commit_path = "%s/%s/%s" % (context, "commit", commitId)
                response = request.get(commit_path, contentType = 'application/json')

                if not response.isSuccessful():
                    print "Failed to fetch commit information from Bitbucket server %s" % server['url']
                    response.errorDump()
                    sys.exit(1)
                else:
                    info = json.loads(response.response)
                    message = info["message"]
                    if messageRegex:
                        message = re.match(messageRegex, message)
                
            print("Bitbucket triggered release for %s-%s" % (branch, commitId))
