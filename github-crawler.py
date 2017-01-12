#!/usr/bin/python
# -*- coding: UTF-8 -*-

import github
import time
import datetime
import wget
import db_operation
import DB_NamedUser
import DB_NamedUser_Followship
import DB_Repository
import hashlib
import os
import random
import udload
import DB_Repository_Assignee
import DB_Repository_Contributor
import DB_Repository_Stargazer
import DB_Repository_Subscriber
import DB_Repository_Watcher
import DB_Commit
import DB_GitCommit
import DB_GitCommit_Parentship
import DB_CommitStatus
import DB_Commit_Parentship
import DB_File
import DB_CommitComment
import DB_Branch
import DB_RepositoryLabel
import DB_Repository_Languages
import DB_Milestone
import DB_Milestone_Label
import DB_Issue
import DB_Issue_Label
import DB_IssueComment
import DB_IssueEvent
import DB_PullRequest
import DB_PullRequestPart
import DB_PullRequestComment
import DB_PullRequest_Commit
import DB_Repository_README
import DB_Tag
import DB_Organization
import DB_RepositoryEvent

# enable debug logging for troubleshooting
#github.enable_console_debug_logging()

"""
    constants
"""
USER_FOLLOW_LEVEL = 0
NUMBERS_OF_PER_PAGE = 30


"""
    global variables
"""
last_stars = 0x7fffffff
start_date = datetime.date(2008, 1, 1)
start_date_week = None
start_date_day = None


g = github.Github("username", "password")

conn = db_operation.connect_to_db_simple()

"""
  check if there is no rate remaining, if so, delay the process until
  rate limit is reset
"""
def sleep_if_no_rate_remaining():
    try:
        
        if g.rate_limiting[0] <= 0:
            time.sleep(g.rate_limiting_resettime - time.time())
    
    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
    except Exception, e:
        print e


"""
    Compute hash value of the specified file
        ...here is sha256...
    Parameters:
        f, file path, type of string
    Return:
        hash value if success otherwise None
"""
def hashfile(f, blocksize=65536):
    try:

        if not os.path.exists(f):
            return None

        afile = open(f, "rb")
        hasher = hashlib.sha256()
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        
        afile.close()
        return hasher.hexdigest()

    except Exception as e:
        print e
        afile.close()
        return None


"""
    inner method
"""
def wget_download_0(link, filepath):
    try:

        sleep_if_no_rate_remaining()
        wget.download(link, filepath)

        return True
    
    except Exception as e:
        print e, 'exception'
        return False


"""
    Download content of the specified link to the specified path  with wget
    Parameters:
        link, url link, type of string
        path, local storage path, type of string 
    Return:
        status, True if success otherwise False
"""
def wget_download(link, filepath):
    try:

        random.seed()

        count = 5
        while count > 0:

            if wget_download_0(link, filepath) and os.path.isfile(filepath):
                break
            
            count = count - 1
            time.sleep(random.randint(1, 10))

        if count > 0:
            return True
        
        return False
    
    except Exception as e:
        print e
        return False


"""
    Crawl a file, which is consisted of:
        Step1, download content of the specifed link to specified path with wget, if success then Step2
        Step2, rename the downloaded file by its hash value and upload to CommonStorage 
        Step3, remove the download file (i.e. the renamed file)
    Parameters:
        link, download url link, type of string
        path, local storage path, type of string
        extension, file extension, type of string
    Return:
        renamed filename if success otherwise None
"""
def wget_upload_clean(link, extension):
    try:

        renamed_filename = None 

        archive_filename = link.split("/")[-1:][0]

        # TODO: what to do when download failture
        if wget_download(link, archive_filename):

            archive_local_url = hashfile(archive_filename)

            if archive_local_url is not None:

                # rename
                archive_local_url = archive_local_url + extension
                os.rename(archive_filename, archive_local_url)

                # upload to common storage
                if udload.upload_to_commonstorage(archive_local_url):
                    renamed_filename = archive_local_url

                # remove
                #time.sleep(10)
                os.remove(archive_local_url)

        return renamed_filename
    
    except Exception as e:
        print e
        return None


"""
    Write content into a new file with specified filename, \
    then rename the file by its hash value and upload to CommonStorage, \
    then remove the local file
    Parameters:
        filename, specified name of the new created file, type of basestring
        content, content that will be writed into, type of basestring
        extension, file extension name, type of basestring
    Return:
        status, True if success otherwise False
"""
def write_upload_clean(filename, content, extension):
    try:

        renamed_filename = None

        f = open(filename+extension, "wb")
        f.write(content)
        f.close()

        local_url = hashfile(filename+extension)

        if local_url is not None:

            local_url = local_url + extension
            os.rename(filename+extension, local_url)

            # upload to common storage
            if udload.upload_to_commonstorage(local_url):
                renamed_filename = local_url
            
            # remove
            #time.sleep(10)
            os.remove(local_url)

        return renamed_filename

    except Exception as e:
        print e
        return None



"""
    Check if the global database connection has been closed, if so, open it again
    Parameters:
    Return:
        status, True if success otherwise False
"""
def open_if_connection_closed():
    global conn

    try:

        if conn is None:
            return False

        if conn.open == 0:
            conn = db_operation.connect_to_db_simple()
            
            if conn is None:
                return False
        
        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
    except Exception, e:
        print e

"""
    Process a GitAuthor, which only contains basic info
    Parameters:
        gitauthor, type of github.GitAuthor.GitAuthor
    Return:
        status, True if success otherwise False
"""
def process_gitauthor(gitauthor):
    try:

        print "\t\t\t\tname", gitauthor.name
        print "\t\t\t\temail", gitauthor.email
        print "\t\t\t\tdate", gitauthor.date

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process a user, crawl its baisc information and relationship information
        ...baisc info...
        ...one level followship info...
    Parameters: 
        user, type of github.NamedUser.NamedUser
        level, the number of levles, type of int
    Return: status, True if success otherwise False
"""
def process_user(user, level):
    try:

        if user is None:
            return True
        
        if open_if_connection_closed() == False:
            return False

        bio = user.bio
        
        db_nameduser = DB_NamedUser.DB_NamedUser(user, conn)
        db_nameduser.save()

        if bio is not None:
            db_nameduser.update_one("bio", bio.replace("'", "\\'").replace('"', '\\"'))
            

        """
        print "\tUSER", '[id', user.id, '; login: ', user.login, '; email:', user.email, ']'
        
        # basic info
        print "\t\ttavatar_url", user.avatar_url
        print "\t\tbio", user.bio
        print "\t\tblog", user.blog
        print "\t\tcollaborators", user.collaborators
        print "\t\tcompany", user.company
        print "\t\tcontributions", user.contributions
        print "\t\tcreated_at", user.created_at
        print "\t\tdisk_usage", user.disk_usage
        print "\t\temail", user.email
        print "\t\tfollowers", user.followers
        print "\t\tfollowing", user.following
        print "\t\tgravatar_id", user.gravatar_id
        print "\t\thireable", user.hireable
        print "\t\turl", user.url
        print "\t\thtml_url", user.html_url
        print "\t\tid", user.id
        print "\t\tlogin", user.login
        print "\t\tname", user.name
        print "\t\tpublic_repos", user.public_repos
        print "\t\ttotal_private_repos", user.total_private_repos
        print "\t\ttype", user.type
        print "\t\tupdated_at", user.updated_at
        """


        """
            followship of the specified level
        """
        if level <= 0:
            return True

        # FOLLOWERS
        sleep_if_no_rate_remaining()
        followers = user.get_followers()
        
        print "\tFOLLOWERS"
        for u in followers:
            #print '\t\t[id', u.id, '; login:', u.login, '; email:', u.email, ']'
            process_user(u, level - 1)
            db_nameduser_followship = DB_NamedUser_Followship.DB_NamedUser_Followship(u, user, conn)
            db_nameduser_followship.save()

        # FOLLOWING
        sleep_if_no_rate_remaining()
        following = user.get_following()

        print "\tFOLLOWING"
        for u in following:
            #print '\t\t[id', u.id, '; login:', u.login, '; email:', u.email, ']'
            process_user(u, level - 1)
            db_nameduser_followship = DB_NamedUser_Followship.DB_NamedUser_Followship(user, u, conn)
            db_nameduser_followship.save()

        return True
    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
    except Exception, e:
        print e



"""
    Process a organization, crawl its basic info and relationship info
        ...basic info...relationship info...
    Parameters:
        org, type of github.Organization.Organization
    Return:
        status, True if success otherwise False
"""
def process_organization(org):
    try:

        if org is None:
            return True

        if open_if_connection_closed() == False:
            return False

        db_organization = DB_Organization.DB_Organization(org, conn)
        db_organization.save()

        """
        print "\t\tavatar_url", org.avatar_url
        print "\t\tbilling_email", org.billing_email
        print "\t\tblog", org.blog
        print "\t\tcollaborators", org.collaborators
        print "\t\tcompany", org.company
        print "\t\tcreated_at", org.created_at
        print "\t\tdisk_usage", org.disk_usage
        print "\t\temail", org.email
        print "\t\tevents_url", org.events_url
        print "\t\tfollowers", org.followers
        print "\t\tfollowing", org.following
        print "\t\tgravatar_id", org.gravatar_id
        print "\t\thtml_url", org.html_url
        print "\t\tid", org.id
        print "\t\tlocation", org.location
        print "\t\tlogin", org.login
        print "\t\tmembers_url", org.members_url
        print "\t\tname", org.name
        print "\t\towned_private_repos", org.owned_private_repos
        print "\t\tpublic_members_url", org.public_members_url
        print "\t\tpublic_repos", org.public_repos
        print "\t\ttotal_private_repos", org.total_private_repos
        print "\t\ttype", org.type
        print "\t\tupdated_at", org.updated_at
        print "\t\turl", org.url
        """
        
        # public members 
        # GithubException 404 {u'documentation_url': u'https://developer.github.com/v3', u'message': u'Not Found'}
        # TODO: consider or not
        #sleep_if_no_rate_remaining()
        #public_members = org.get_public_members()

        #print "\t\tORGANIZATIONPUBLICMEMBERS"
        #for member in public_members:
        #    process_user(member, USER_FOLLOW_LEVEL)


        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process a branch, crawl its name and corresponding commit
    Parameters: 
        repo, type of github.Repository.Repository
        branch, type of github.Branch.Branch
    Return: 
        status, True if success otherwise False
"""
def process_branch(repo, branch):
    try:

        if branch is None:
            return False

        if open_if_connection_closed() == False:
            return False
        
        db_branch = DB_Branch.DB_Branch(branch, repo, conn)
        db_branch.save()
        
        print '\t[name:', branch.name, '; sha:', branch.commit.sha, ']'

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process branches of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_branches(repo):
    try:

        if repo is None:
            return False

        sleep_if_no_rate_remaining()
        branches = repo.get_branches()

        print "\tBRANCHES"
        for i in range(0, branches._lenOfFirstPage()):
            branch = branches[i]
            process_branch(repo, branch)

        page = 0
        while True:
            if branches._couldGrow() == False:
                break

            branches_per_page = None
            sleep_if_no_rate_remaining()
            branches_per_page = branches._fetchNextPage()

            if branches_per_page is None:
                continue

            for branch in branches_per_page:
                process_branch(repo, branch)
            
        """
        print "\tBRANCHES"
        for branch in branches:
            process_branch(repo, branch)
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process a CommitComment, crawl its basic info and related author
        ...basic info and related author...
    Parameters:
        commit, type of github.Commit.Commit
        comment, type of github.CommitComment.CommitComment
    Return: 
        status, True if success otherwise False
"""
def process_commitcomment(commit, comment):
    try:

        if comment is None:
            return False

        if open_if_connection_closed() == False:
            return False

        db_commitcomment = DB_CommitComment.DB_CommitComment(commit, comment, conn)
        db_commitcomment.save()

        """
        # basic info
        print "\t\t\tid", comment.id
        print "\t\t\turl", comment.url
        print "\t\t\thtml_url", comment.html_url
        print "\t\t\tcommit_id", comment.commit_id
        print "\t\t\tpath", comment.path
        print "\t\t\tline", comment.line
        print "\t\t\tposition", comment.position
        print "\t\t\tbody [", comment.body, ']'
        print "\t\t\tcreated_at", comment.created_at
        print "\t\t\tupdated_at", comment.updated_at
        """

        # author
        author = comment.user
        print "\t\t\tCOMMITAUTHOR"
        process_user(author, USER_FOLLOW_LEVEL)

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process comments of one commit
    Parameters:
        commit, type of github.Commit.Commit
    Return:
        status, True if success otherwise False
"""
def process_commitcomments(commit):
    try:

        if commit is None:
            return False

        sleep_if_no_rate_remaining()
        comments = commit.get_comments()

        for i in range(0, comments._lenOfFirstPage()):
            comment = comments[i]
            process_commitcomment(commit, comment)

        page = 0
        while True:
            if comments._couldGrow() == False:
                break

            comments_per_page = None
            sleep_if_no_rate_remaining()
            comments_per_page = comments._fetchNextPage()

            if comments_per_page is None:
                continue

            for comment in comments_per_page:
                process_commitcomment(commit, comment)
            

        """
        print "\t\tCOMMITCOMMENTS"
        for comment in comments:
            process_commitcomment(commit, comment)
        """

        return True

    except Exception as e:
        print e
        return False



"""
    Process a CommitFile
    Parameters:
        f, type of github.File.File
        commit, type of github.Commit.Commit
    Return:
        status, True if success otherwise False
"""
def process_commitfile(f, commit):
    try:

        if f is None:
            return False
        
        if open_if_connection_closed() == False:
            return False

        db_file = DB_File.DB_File(f, commit, conn)
        db_file.save()

        """
        print "\t\t\tsha", f.sha
        print "\t\t\tfilename", f.filename
        print "\t\t\tstatus", f.status
        print "\t\t\tadditions", f.additions
        print "\t\t\tdeletions", f.deletions
        print "\t\t\tchanges", f.changes
        print "\t\t\traw_url", f.raw_url
        print "\t\t\tblob_url", f.blob_url
        print "\t\t\tcontents_url", f.contents_url
        #print "\t\t\tpatch [", f.patch, ']'
        """

        if f.patch is None:
            return True

        # patch
        print "\t\tpatch"
        patch_local_url = write_upload_clean(f.sha, f.patch, ".patch")
        if patch_local_url is not None:
            db_file.update_one("patch_local_url", patch_local_url)

        """
        print "\t\t\tdownloading", (f.sha + '_' + f.filename), '...'
        extension = "." + f.filename.split(".")[-1:][0]
        raw_local_url = wget_upload_clean(f.raw_url, extension)
        if raw_local_url is not None:
            db_file.update_one("raw_local_url", raw_local_url)
        """
        
        #wget.download(f.raw_url, f.sha + '_' + f.filename.split("/")[-1:][0])
        #print 'done'

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process files related with one commit
    Parameters:
        commit, type of github.Commit.Commit
    Return:
        status, True if success otherwise False
"""
def process_commit_files(commit):
    try:

        if commit is None:
            return False

        files = commit.files

        print "\t\tFILES"
        for f in files:
            process_commitfile(f, commit)

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process a CommitStatus
        ...basic info and creator...
    Parameters: 
        status, type of github.CommitStatus.CommitStatus
    Return:
        status, True if success otherwise False
"""
def process_commitstatus(status, commit):
    try:
        if status is None:
            return False
        
        if open_if_connection_closed() == False:
            return False

        db_commitstatus = DB_CommitStatus.DB_CommitStatus(status, commit, conn)
        db_commitstatus.save()
    
        """
        # basic info
        print "\t\t\tid", status.id
        print "\t\t\turl", status.url
        print "\t\t\ttarget_url", status.target_url
        print "\t\t\tdescription", status.description
        print "\t\t\tstate", status.state
        print  "\t\t\tcreated_at", status.created_at
        print "\t\t\tupdated_at", status.updated_at
        """

        # creator
        creator = status.creator

        print "\t\t\tcreator"
        process_user(creator, USER_FOLLOW_LEVEL)

        return True
    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process statuses of one commit
    Parameters:
        commit, type of github.Commit.Commit
    Return:
        status, True if success otherwise False
"""
def process_commit_statuses(commit):
    try:

        sleep_if_no_rate_remaining()
        statuses = commit.get_statuses()

        for i in range(0, statuses._lenOfFirstPage()):
            status = commits[i]
            process_commitstatus(status, commit)

        while True:
            if statuses._couldGrow() == False:
                break

            statuses_per_page = None
            sleep_if_no_rate_remaining()
            statuses_per_page = statuses._fetchNextPage()

            if statuses_per_page is None:
                continue

            for status in statuses_per_page:
                process_commitstatus(status, commit)
            
        """
        print "\t\tCOMMITSTATUS", statuses.totalCount
        for status in statuses:
            process_commitstatus(status, commit)
        """

        return True
    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process parent gitcommits of one gitcommit
        ...crawl all the parent-ship...
    Parameters:
        child, type of github.GitCommit.GitCommit
        parents, type of list of github.GitCommit.GitCommit
    Return:
        status, True if success otherwise False
"""
def process_gitcommit_parents(child, parents):
    try:

        if open_if_connection_closed() == False:
            return False

        for parent in parents:

            db_gitcommit_parentship = DB_GitCommit_Parentship.DB_GitCommit_Parentship(parent, child, conn)
            db_gitcommit_parentship.save()


        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False

"""
    Process a gitcommit, a gitcommit is a inside object of a commit
        ...basic info and parents info...
    Parameters:
        gitcommit, type of github.GitCommit.GitCommit
    Return:
        status, True if success otherwise False
"""

def process_gitcommit(gitcommit):
    try:

        if open_if_connection_closed() == False:
            return False

        db_gitcommit = DB_GitCommit.DB_GitCommit(gitcommit, conn)
        db_gitcommit.save()

        """
        # basic info
        print "\t\t\tsha", gitcommit.sha
        print "\t\t\turl", gitcommit.url
        print "\t\t\thtml_url", gitcommit.html_url
        print "\t\t\tmessage [", gitcommit.message, ']'

        # author and committer
        print "\t\t\tGITAUTHOR"
        process_gitauthor(gitcommit.author)
        process_gitauthor(gitcommit.committer)
        """        

        # parents ship
        parents = gitcommit.parents        

        print "\t\t\tparents"
        process_gitcommit_parents(gitcommit, parents)
        

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False

"""
    Process parent-child relationship between 2 github.Commit.Commit
    Parameters:
        child, child commit, type of github.Commit.Commit
    Return:
        status, True if success otherwise False
"""
def process_commit_parents(child):
    try:

        if child is None:
            return False
        
        if open_if_connection_closed() == False:
            return False
        
        # 1-level parents ship
        parents = child.parents
        for parent in parents:
            #print "\t\tparent [sha:", parent.sha, ']'

            db_commit_parentship = DB_Commit_Parentship.DB_Commit_Parentship(parent, child, conn)
            db_commit_parentship.save()

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False




"""
    Process a commit
        ......
    Parameters:
        commit, type of github.Commit.Commit
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_commit(commit, repo):
    try:

        #print "\t[sha:", commit.sha, ']'

        if open_if_connection_closed() == False:
            return False


        db_commit = DB_Commit.DB_Commit(commit,repo, conn)
        db_commit.save()

        """
        # basic info
        print ''
        print "\t\turl", commit.url
        print "\t\thtml_url", commit.html_url
        print "\t\tcomments_url", commit.comments_url
        """

        # GitCommit
        gitcommit = commit.commit
        
        print "\t\tGITCOMMIT"
        process_gitcommit(gitcommit)


        """
        # STATS [additions, deletions, total]
        stats = commit.stats
        print "\t\tstats [additions:", stats.additions, ', deletions:', stats.deletions, ', total:', stats.total, ']'
        """


        # COMMITSTATUSES
        process_commit_statuses(commit)


        # 1-level parents ship
        process_commit_parents(commit)


        # FILES
        process_commit_files(commit)


        # CommitComments
        process_commitcomments(commit)

        
        # AUTHOR and COMMITTER
        process_user(commit.author, USER_FOLLOW_LEVEL)
        process_user(commit.committer, USER_FOLLOW_LEVEL)

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False





"""
    Process commits of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_commits(repo):
    try:

        if repo is None:
            return False
        
        sleep_if_no_rate_remaining()
        commits = repo.get_commits()


        print "\tCOMMITS"
        for i in range(0, commits._lenOfFirstPage()):
            commit = commits[i]
            process_commit(commit, repo)

        page = 0
        while True:
            if commits._couldGrow() == False:
                break

            commits_per_page = None
            sleep_if_no_rate_remaining()
            commits_per_page = commits._fetchNextPage()

            if commits_per_page is None:
                continue

            for commit in commits_per_page:
                process_commit(commit, repo)
            
            print "page", page
            page = page + 1
            

        """
        i = 0
        print "\tCOMMITS"
        for commit in commits:
            print commit.sha, i
            i = i + 1
            #process_commit(commit, repo)
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process a label, which just includes 2 basic info
        ...basic info [color, name]
    Parameters:
        milestone, type of github.Milestone.Milestone
        label, type of github.Label.Label
    Return:
        status, True if success otherwise False
"""
def process_milestone_label(milestone, label):
    try:

        if label is None:
            return True

        if open_if_connection_closed() == False:
            return False

        db_milestone_label = DB_Milestone_Label.DB_Milestone_Label(label, milestone, conn)
        db_milestone_label.save()

        """
        # TODO: where id? if unique? maybe related to isssue (issue_id as FK)
        print "\t\t\tname", label.name
        print "\t\t\tcolor", label.color
        print "\t\t\turl", label.url
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process labels of one milestone
    Parameters:
        milestone, type of github.Milestone.Milestone
    Return:
        status, True if success otherwise False
"""
def process_milestone_labels(milestone):
    try:

        if milestone is None:
            return False
        
        sleep_if_no_rate_remaining()
        labels = milestone.get_labels()

        print "\t\t\tMILESTONELABELS"
        for label in labels:
            process_milestone_label(milestone, label)

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process a milestone, crawl its baisc info
        ...basic info...
    Parameters:
        milestone, type of github.Milestone.Milestone
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_milestone(milestone, repo):
    try:

        if milestone is None:
            return True
        
        if open_if_connection_closed() == False:
            return False

        db_milestone = DB_Milestone.DB_Milestone(milestone, repo, conn)
        db_milestone.save()

        """
        print "\t\t\tid", milestone.id
        print "\t\t\tnumber", milestone.number
        print "\t\t\turl", milestone.url
        print "\t\t\ttitle [", milestone.title, ']'
        print "\t\t\tdescription [", milestone.description, ']'
        print "\t\t\tstate", milestone.state
        print "\t\t\topen_issues", milestone.open_issues
        print "\t\t\tclosed_issues", milestone.closed_issues
        print "\t\t\tcreated_at", milestone.created_at
        print "\t\t\tupdated_at", milestone.updated_at
        print "\t\t\tdue_on", milestone.due_on
        """

        
        # labels
        process_milestone_labels(milestone)
        
        # creator
        creator = milestone.creator
        print "\t\t\tMILESTONECREATOR"
        if creator is not None:
            process_user(creator, USER_FOLLOW_LEVEL)

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process milestones of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_milestones(repo):
    try:

        if repo is None:
            return False

        sleep_if_no_rate_remaining()
        milestones = repo.get_milestones()

        print "\tMILESTONES"
        for i in range(0, milestones._lenOfFirstPage()):
            milestone = milestones[i]
            process_milestone(milestone, repo)

        page = 0
        while True:
            if milestones._couldGrow() == False:
                break

            milestones_per_page = None
            sleep_if_no_rate_remaining()
            milestones_per_page = milestones._fetchNextPage()

            if milestones_per_page is None:
                continue

            for milestone in milestones_per_page:
                process_milestone(milestone, repo)
            
        
        """
        print "\tMILESTONES"
        for milestone in milestones:
            process_milestone(milestone, repo)
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False




"""
    Process a label, which just includes 2 basic info
        ...basic info [color, name]
    Parameters:
        label, type of github.Label.Label
    Return:
        status, True if success otherwise False
"""
def process_label(label):
    try:

        if label is None:
            return True

        # TODO: where id? if unique? maybe related to isssue (issue_id as FK)
        print "\t\t\tname", label.name
        print "\t\t\tcolor", label.color
        print "\t\t\turl", label.url

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process a label of one repository, which just includes 2 basic info
        ...basic info [color, name]
    Parameters:
        repo, type of github.Repository.Repository
        label, type of github.Label.Label
    Return:
        status, True if success otherwise False
"""
def process_repo_label(repo, label):
    try:

        if label is None:
            return True

        if open_if_connection_closed() == False:
            return False

        db_repositorylabel = DB_RepositoryLabel.DB_RepositoryLabel(repo, label, conn)
        db_repositorylabel.save()

        """
        # TODO: where id? if unique? maybe related to isssue (issue_id as FK)
        print "\t\t\tname", label.name
        print "\t\t\tcolor", label.color
        print "\t\t\turl", label.url
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process labels of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_repo_labels(repo):
    try:

        if repo is None:
            return False
        
        sleep_if_no_rate_remaining()
        labels = repo.get_labels()

        for i in range(0, labels._lenOfFirstPage()):
            label = labels[i]
            process_repo_label(repo, label)

        while True:
            if labels._couldGrow() == False:
                break

            labels_per_page = None
            sleep_if_no_rate_remaining()
            labels_per_page = labels._fetchNextPage()

            if labels_per_page is None:
                continue

            for label in labels_per_page:
                process_repo_label(repo, label)
            
        """
        print "\tLABELS"
        for label in labels:
            process_repo_label(repo, label)
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process a IssueEvent, crawl its basic info (not include payload) and actor user
        ...basic info ...actor...
    Parameters:
        event, type of github.IssueEvent.IssueEvent
        issue, type of github.Issue.Issue        
    Return:
        status, True if success otherwise False
"""
def process_issueevent(event, issue):
    try:

        if event is None:
            return True

        if open_if_connection_closed() == False:
            return False

        db_issueevent = DB_IssueEvent.DB_IssueEvent(event, issue, conn)
        db_issueevent.save()

        """
        print "\t\t\tISSUEEVENT"
        print "\t\t\tid", event.id
        print "\t\t\turl", event.url
        print "\t\t\tevent", event.event
        print "\t\t\tcommit_id", event.commit_id
        print "\t\t\tcreated_at", event.created_at
        """
        
        # issue
        issue = event.issue
        if issue is not None:
            print "\t\t\tissue_id", issue.id

        # actor
        actor = event.actor
        print "\t\t\tISSUEEVENTACTOR"
        if actor is not None:
            process_user(actor, USER_FOLLOW_LEVEL)

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process events of one issue
    Parameters:
        issue, type of github.Issue.Issue
    Return:
        status, True if success otherwise False
"""
def process_issueevents(issue):
    try:

        if issue is None:
            return True
        
        sleep_if_no_rate_remaining()
        events = issue.get_events()

        print "\t\tISSUEEVENTS"
        for i in range(0, events._lenOfFirstPage()):
            event = events[i]
            process_issueevent(event, issue)

        page = 0
        while True:
            if events._couldGrow() == False:
                break

            events_per_page = None
            sleep_if_no_rate_remaining()
            events_per_page = events._fetchNextPage()

            if events_per_page is None:
                continue

            for event in events_per_page:
                process_issueevent(event, issue)
            

        """
        print "\t\tISSUEEVENTS"
        for event in events:
            process_issueevent(event, issue)
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process a IssueComment, crawl its basic info and a related user
        ...basic info ...realated user...
    Parameters:
        comment, type of github.IssueComment.IssueComment
        issue, type of github.Issue.Issue
    Return:
        status, True if success otherwise False
"""
def process_issuecomment(comment, issue):
    try:

        if comment is None:
            return True

        if open_if_connection_closed() == False:
            return False

        db_issuecomment = DB_IssueComment.DB_IssueComment(comment, issue, conn)
        db_issuecomment.save()
    
        """
        print "\t\t\tISSUECOMMENT"
        print "\t\t\tid", comment.id
        print "\t\t\turl", comment.url
        print "\t\t\thtml_url", comment.html_url
        print "\t\t\tissue_url", comment.issue_url
        print "\t\t\tbody [", comment.body, ']'
        print "\t\t\tcreated_at", comment.created_at
        print "\t\t\tupdated_at", comment.updated_at
        """

        # author
        user = comment.user

        print "\t\t\tISSUECOMMENTUSER"
        if user is not None:
            process_user(user, USER_FOLLOW_LEVEL)

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process comments of one issue
    Parameters:
        issue, type of github.Issue.Issue
    Return:
        status, True if success otherwise False
"""
def process_issuecomments(issue):
    try:

        if issue is None:
            return False

        sleep_if_no_rate_remaining()
        comments = issue.get_comments()

        print "\t\tISSUECOMMENTS"
        for i in range(0, comments._lenOfFirstPage()):
            comment = comments[i]
            process_issuecomment(comment, issue)

        while True:
            if comments._couldGrow() == False:
                break

            comments_per_page = None
            sleep_if_no_rate_remaining()
            comments_per_page = comments._fetchNextPage()

            if comments_per_page is None:
                continue

            for comment in comments_per_page:
                process_issuecomment(comment, issue)
            
        """
        print "\t\tISSUECOMMENTS"
        for comment in comments:
            process_issuecomment(comment, issue)
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process a label of one issue, which just includes 2 basic info
        ...basic info [color, name]
    Parameters:
        label, type of github.Label.Label
        issue, type of github.Issue.Issue
    Return:
        status, True if success otherwise False
"""
def process_issue_label(label, issue):
    try:

        if label is None:
            return True

        if open_if_connection_closed() == False:
            return False

        db_issue_label = DB_Issue_Label.DB_Issue_Label(label, issue, conn)
        db_issue_label.save()

        """
        # TODO: where id? if unique? maybe related to isssue (issue_id as FK)
        print "\t\t\tname", label.name
        print "\t\t\tcolor", label.color
        print "\t\t\turl", label.url
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process labels of one issue
    Parameters:
        issue, type of github.Issue.Issue
    Return:
        status, True if success otherwise False
"""
def process_issue_labels(issue):
    try:

        if issue is None:
            return False

        sleep_if_no_rate_remaining()
        labels = issue.get_labels()

        print "\t\tLABELS"
        for i in range(0, labels._lenOfFirstPage()):
            label = labels[i]
            process_issue_label(label, issue)

        while True:
            if labels._couldGrow() == False:
                break

            labels_per_page = None
            sleep_if_no_rate_remaining()
            labels_per_page = labels._fetchNextPage()

            if labels_per_page is None:
                continue

            for label in labels_per_page:
                process_issue_label(label, issue)
            
        """
        print "\t\tLABELS"
        for label in labels:
            process_issue_label(label, issue)
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process a issue, crawl its basic info, related users and comments
        ...basic info ...related users ...comments
    Parameters:
        issue, type of github.Issue.Issue
    Return:
        status, True if success otherwise False
"""
def process_issue(issue, repo):
    try:
        
        if issue is None:
            return False

        if open_if_connection_closed() == False:
            return False

        db_issue = DB_Issue.DB_Issue(issue, repo, conn)
        db_issue.save()

        """
        print "ISSUE BASIC INFO"

        # basic info
        print "\t\tid", issue.id
        print "\t\tnumber", issue.number
        print "\t\turl", issue.url
        print "\t\thtml_url", issue.html_url
        print "\t\tcomments_url", issue.comments_url
        print "\t\tevents_url", issue.events_url
        print "\t\tlabels_url", issue.labels_url
        print "\t\ttitle [", issue.title, ']'
        print "\t\tbody [", issue.body, ']'
        print "\t\tcomments", issue.comments
        print "\t\tstate", issue.state
        print "\t\tcreated_at", issue.created_at
        print "\t\tclosed_at", issue.closed_at
        """

        # ASSIGNEE
        assignee = issue.assignee
        print "\t\tISSUEASSIGNEE"
        if assignee is not None:
            process_user(assignee, USER_FOLLOW_LEVEL)

        # CLOSED_BY
        closed_by = issue.closed_by
        print "\t\tISSUECLOSED_BY"
        if closed_by is not None:
            process_user(closed_by, USER_FOLLOW_LEVEL)

        # User 
        user = issue.user
        print "\t\tISSUEUSER"
        if user is not None:
            process_user(user, USER_FOLLOW_LEVEL)


        # labels
        process_issue_labels(issue)

        # comments
        process_issuecomments(issue)
        
        # events
        process_issueevents(issue)

        
        # milestone
        #milestone = issue.milestone
        #print "\t\tMILESTONE"
        #if milestone is not None:
        #    process_milestone(milestone)


        # possible corresponding pull request
        #pull = issue.pull_request
        #
        #if pull is not None:
        #    print "\t\tPULL"

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process issues of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_issues(repo):
    try:

        if repo is None:
            return False

        sleep_if_no_rate_remaining()
        issues = repo.get_issues()

        print "\tISSUES"
        for i in range(0, issues._lenOfFirstPage()):
            issue = issues[i]
            process_issue(issue, repo)

        while True:
            if issues._couldGrow() == False:
                break

            issues_per_page = None
            sleep_if_no_rate_remaining()
            issues_per_page = issues._fetchNextPage()

            if issues_per_page is None:
                continue

            for issue in issues_per_page:
                process_issue(issue, repo)
    


        sleep_if_no_rate_remaining()
        issues = repo.get_issues(state='closed')

        print "\tCLOSEDISSUES"
        for i in range(0, issues._lenOfFirstPage()):
            issue = issues[i]
            process_issue(issue, repo)

        while True:
            if issues._couldGrow() == False:
                break

            issues_per_page = None
            sleep_if_no_rate_remaining()
            issues_per_page = issues._fetchNextPage()

            if issues_per_page is None:
                continue

            for issue in issues_per_page:
                process_issue(issue, repo)
        
        """
        print "\tISSUES"
        for issue in issues:
            process_issue(issue, repo)
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process a PullRequestComment, crawl its basic info 
        ...basic info ...
    Parameters:
        pullcomment, type of github.PullRequestComment.PullRequestComment
        pull, type of github.PullRequest.PullRequest
    Return:
        status, True if success otherwise False
"""
def process_pullcomment(pullcomment, pull):
    try:

        if pullcomment is None:
            return True

        if open_if_connection_closed() == False:
            return False

        db_pullrequestcomment = DB_PullRequestComment.DB_PullRequestComment(pullcomment, pull, conn)
        db_pullrequestcomment.save()

        if pullcomment.diff_hunk is not None:
            diff_hunk_local_url = write_upload_clean(str(pullcomment.id), pullcomment.diff_hunk, ".diff")
            if diff_hunk_local_url is not None:
                db_pullrequestcomment.update_one("diff_hunk_local_url", diff_hunk_local_url)

        """
        print "\t\t\tid", pullcomment.id
        print "\t\t\turl", pullcomment.url
        print "\t\t\thtml_url", pullcomment.html_url
        print "\t\t\tcommit_id", pullcomment.commit_id
        print "\t\t\toriginal_commit_id", pullcomment.original_commit_id
        print "\t\t\tpath", pullcomment.path
        print "\t\t\tposition", pullcomment.position
        print "\t\t\toriginal_position", pullcomment.original_position
        print "\t\t\tbody [", pullcomment.body, ']'
        print "\t\t\tdiff_hunk [", pullcomment.diff_hunk, ']'
        print "\t\t\tcreated_at", pullcomment.created_at
        print "\t\t\tupdated_at", pullcomment.updated_at

        print "\t\t\tpull_request_url", pullcomment.pull_request_url
        """


        # user
        user = pullcomment.user

        if user is not None:
            print "\t\t\tPULLREQUESTCOMMENTUSER"
            process_user(user, USER_FOLLOW_LEVEL)

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process comments of github.PullRequest.PullRequest
    Parameters:
        pull, type of github.PullRequest.PullRequest
    Return:
        status, True if success otherwise False
"""
def process_pullcomments(pull):
    try:

        if pull is None:
            return True

        print "\t\tcomments", pull.comments

        sleep_if_no_rate_remaining()
        pull_comments = pull.get_comments()

        for i in range(0, pull_comments._lenOfFirstPage()):
            pc = pull_comments[i]
            process_pullcomment(pc, pull)

        while True:
            if pull_comments._couldGrow() == False:
                break

            pull_comments_per_page = None
            sleep_if_no_rate_remaining()
            pull_comments_per_page = pull_comments._fetchNextPage()

            if pull_comments_per_page is None:
                continue

            for pc in pull_comments_per_page:
                process_pullcomment(pc, pull)
            

        """
        # TODO: need to confirm if they are 0 length
        for pc in pull_comments:
            process_pullcomment(pc, pull)
        """
        
        # review_comments, type of github.PaginatedList.PaginatedList of github.PullRequestComment.PullRequestComment
        print "\t\treview_comments", pull.review_comments

        sleep_if_no_rate_remaining()
        review_comments = pull.get_review_comments()

        for i in range(0, review_comments._lenOfFirstPage()):
            rc = review_comments[i]
            process_pullcomment(rc, pull)

        while True:
            if review_comments._couldGrow() == False:
                break

            review_comments_per_page = None
            sleep_if_no_rate_remaining()
            review_comments_per_page = review_comments._fetchNextPage()

            if review_comments_per_page is None:
                continue

            for rc in review_comments_per_page:
                process_pullcomment(rc, pull)
            

        """
        for rc in review_comments:
            process_pullcomment(rc, pull)
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process a PullRequestPart, crawl basic info and related user
        ...basic info ...related user...
    Parameters:
        pullpart, type of github.PullRequestPart.PullRequestPart
    Return:
        status, True if success otherwise False
"""
def process_pullpart(pullpart):
    try:

        if pullpart is None:
            return True

        if open_if_connection_closed() == False:
            return False

        db_pullrequestpart = DB_PullRequestPart.DB_PullRequestPart(pullpart, conn)
        db_pullrequestpart.save()
        
        """
        print "\t\t\tsha", pullpart.sha
        print "\t\t\tref", pullpart.ref
        print "\t\t\tlabel", pullpart.label

        # repository (FK)
        repo = pullpart.repo

        if repo is not None:
            print "\t\t\trepository [id:", repo.id, '; name:', repo.name, ']'
        """
        

        # user
        user = pullpart.user

        if user is not None:
            print "\t\t\tPULLREQUESTPARTUSER"
            process_user(user, USER_FOLLOW_LEVEL)


        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process commits of one pullrequest
    Parameters:
        pull, type of github.PullRequest
    Return:
        status, True if success otherwise False
"""
def process_pull_commits(pull):
    try:

        if pull is None:
            return True

        if open_if_connection_closed() == False:
            return False
        
        """
        print "\t\tcommits_url", pull.commits_url
        print "\t\tcommits", pull.commits
        """

        sleep_if_no_rate_remaining()
        commits = pull.get_commits()

        for i in range(0, commits._lenOfFirstPage()):
            commit = commits[i]
            db_pullrequest_commit = DB_PullRequest_Commit.DB_PullRequest_Commit(commit, pull, conn)
            db_pullrequest_commit.save()

        while True:
            if commits._couldGrow() == False:
                break

            commits_per_page = None
            sleep_if_no_rate_remaining()
            commits_per_page = commits._fetchNextPage()

            if commits_per_page is None:
                continue

            for commit in commits_per_page:
                db_pullrequest_commit = DB_PullRequest_Commit.DB_PullRequest_Commit(commit, pull, conn)
                db_pullrequest_commit.save()
            

        """
        # TODO: may be just FK
        for commit in commits:           
            print "\t\tcommit_sha [", commit.sha, ']'

            if commit is None:
                continue

            db_pullrequest_commit = DB_PullRequest_Commit.DB_PullRequest_Commit(commit, pull, conn)
            db_pullrequest_commit.save()
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process a pull request of a repository
        ...
    Parameters:
        pull, type of github.PullRequest.PullRequest
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_pull(pull, repo):
    try:

        if pull is None:
            return True

        if open_if_connection_closed() == False:
            return False

        db_pullrequest = DB_PullRequest.DB_PullRequest(pull, repo, conn)
        db_pullrequest.save()

        patch_local_url = wget_upload_clean(pull.patch_url, ".patch") if pull.patch_url is not None else None
        if patch_local_url is not None:
            db_pullrequest.update_one("patch_local_url", patch_local_url)
        
        print "PULL"
        
        """
        print "\t\tid", pull.id
        print "\t\turl", pull.url
        print "\t\thtml_url", pull.html_url
        print "\t\tcomments_url", pull.comments_url
        # TODO: extract the corresponding issue identifier
        print "\t\tissue_url", pull.issue_url
        print "\t\tpatch_url", pull.patch_url
        print "\t\tdiff_url", pull.diff_url
        print "\t\treview_comment_url", pull.review_comment_url
        print "\t\treview_comments_url", pull.review_comments_url
        print "\t\tadditions", pull.additions
        print "\t\tdeletions", pull.deletions
        print "\t\ttitle, [", pull.title, ']'
        print "\t\tbody, [", pull.body, ']'
        print "\t\tcreated_at", pull.created_at
        print "\t\tupdated_at", pull.updated_at
        print "\t\tclosed_at", pull.closed_at
        print "\t\tstate", pull.state
        
        print "\t\tmerge_commit_sha", pull.merge_commit_sha
        print "\t\tmergeable", pull.mergeable
        print "\t\tmergeable_state", pull.mergeable_state
        print "\t\tmerged", pull.merged
        print "\t\tmerged_at", pull.merged_at
        """

       
        # assignee
        assignee = pull.assignee
        if assignee is not None:
            print "\t\tPULLREQUESTASSIGNEE"
            process_user(assignee, USER_FOLLOW_LEVEL)

        merged_by = pull.merged_by
        print "\t\tPULLREQUESTMERGED_BY"
        if merged_by is not None:
            process_user(merged_by, USER_FOLLOW_LEVEL)

        
        # milestone (FK)
        #milestone = pull.milestone
        #if milestone is not None:
        #    print "\t\tmilestone", milestone.id
        
        # base and head
        base = pull.base
        
        print "\t\tBASE"
        if base is not None:
            process_pullpart(base)
        
        head = pull.head

        print "\t\tHEAD"
        if head is not None:
            process_pullpart(head)
             
        
        # comments and review_comments, type of github.PaginatedList.PaginatedList of github.PullRequestComment.PullRequestComment
        process_pullcomments(pull)       


        # commits
        process_pull_commits(pull)
        
        
        """
        # changed files, CAN BE RETRIVED FROM ITS RELATED COMMITS
        #print "\t\tchanged_files", pull.changed_files
        #
        #sleep_if_no_rate_remaining()
        #changed_files = pull.get_files()
        #
        # may be just as FK and output f.sha, similar to 'repo.commits 2 pull.commits''
        #for f in changed_files:
        #    process_commitfile(f)
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process pulls of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_pulls(repo):
    try:

        if repo is None:
            return True

        sleep_if_no_rate_remaining()
        pulls = repo.get_pulls()

        print "\tPULLS"
        for i in range(0, pulls._lenOfFirstPage()):
            pull = pulls[i]
            process_pull(pull, repo)

        page = 0
        while True:
            if pulls._couldGrow() == False:
                break

            pulls_per_page = None
            sleep_if_no_rate_remaining()
            pulls_per_page = pulls._fetchNextPage()

            if pulls_per_page is None:
                continue

            for pull in pulls_per_page:
                process_pull(pull, repo)
            

        sleep_if_no_rate_remaining()
        pulls = repo.get_pulls(state='closed')

        print "\tCLOSED PULLS"
        for i in range(0, pulls._lenOfFirstPage()):
            pull = pulls[i]
            process_pull(pull, repo)

        page = 0
        while True:
            if pulls._couldGrow() == False:
                break

            pulls_per_page = None
            sleep_if_no_rate_remaining()
            pulls_per_page = pulls._fetchNextPage()

            if pulls_per_page is None:
                continue

            for pull in pulls_per_page:
                process_pull(pull, repo)


        """
        print "\tPULLS"
        for pull in pulls:
            process_pull(pull, repo)
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process a ContentFile, crawl its basic info and related entities
        ...basic info ...related entities..
    Parameters:
        cf, type of github.ContentFile.ContentFile
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_contentfile(cf, repo):
    try:

        if cf is None:
            return True

        if open_if_connection_closed() == False:
            return False

        db_repository_readme = DB_Repository_README.DB_Repository_README(cf, repo, conn)
        db_repository_readme.save()

        """
        print "\t\tsha", cf.sha
        print "\t\tname", cf.name
        print "\t\turl", cf.url
        print "\t\thtml_url", cf.html_url
        print "\t\tgit_url", cf.git_url
        print "\t\tpath", cf.path
        print "\t\ttype", cf.type
        print "\t\tencoding", cf.encoding
        print "\t\tcontent [", cf.content, ']'
        print "\t\tsize", cf.size
        """

        filename = cf.sha + '_' + cf.name

        content_local_url = write_upload_clean(filename, cf.content, ".md")
        if content_local_url is not None:
            db_repository_readme.update_one("content_local_url", content_local_url)
        
        #f = open(filename, 'w')
        #f.write(cf.content)
        #f.close()
        

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process README of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_readme(repo):
    try:

        if repo is None:
            return True

        sleep_if_no_rate_remaining()
        readme = repo.get_readme()

        print "\tREADME"
        process_contentfile(readme, repo)

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process a RepositoryKey, crawl its basic info
        ...basic info...
    Parameters:
        key, type of github.RepositoryKey.RepositoryKey
    Return:
        status, True if success otherwise False
"""
def process_key(key):
    try:

        if key is None:
            return True

        print "\t\tid", key.id
        print "\t\turl", key.url
        print "\t\ttitle", key.title
        print "\t\tkey", key.key
        print "\t\tverified", key.verified

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Process a Tag
        ...
    Parameters:
        tag, type of github.Tag.Tag
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_tag(tag, repo):
    try:

        if tag is None:
            return True

        if open_if_connection_closed() == False:
            return False

        db_tag = DB_Tag.DB_Tag(tag, repo, conn)
        db_tag.save()

        """
        print "\t\tname", tag.name
        print "\t\ttarball_url", tag.tarball_url
        print "\t\tzipball_url", tag.zipball_url
        """

        zipball_local_url = wget_upload_clean(tag.zipball_url, ".zip")
        if zipball_local_url is not None:
            db_tag.update_one("zipball_local_url", zipball_local_url)

        """
        wget.download(tag.zipball_url)
        # corresponding commit, which is only responsible for the creation of this tag
        commit = tag.commit

        if commit is not None:
            print "\t\tcommit [sha:", commit.sha, '; date:', commit.commit.committer.date, ']'
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process tags of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_tags(repo):
    try:

        if repo is None:
            return True

        sleep_if_no_rate_remaining()
        tags = repo.get_tags()

        print "\tTAGS"
        for i in range(0, tags._lenOfFirstPage()):
            tag = tags[i]
            process_tag(tag, repo)

        while True:
            if tags._couldGrow() == False:
                break

            tags_per_page = None
            sleep_if_no_rate_remaining()
            tags_per_page = tags._fetchNextPage()

            if tags_per_page is None:
                continue

            for tag in tags_per_page:
                process_tag(tag, repo)
            
        """
        print "\tTAGS"
        for tag in tags:
            process_tag(tag, repo)
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Process a Repository Event,
        ...
    Parameters:
        event, type of github.Event.Event
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_repoevent(event, repo):
    try:

        if event is None:
            return True

        if open_if_connection_closed() == False:
            return False

        db_repositoryevent = DB_RepositoryEvent.DB_RepositoryEvent(event, repo, conn)
        db_repositoryevent.save()

        """
        print "\t\tid", event.id
        print "\t\ttype", event.type
        print "\t\tpublic",event.public
        print "\t\tcreated_at", event.created_at
        #print "\t\tpayload [", event.payload, ']'
        """
        

        # actor
        actor = event.actor
        if actor is not None:
            print "\t\tACTOR"
            process_user(actor, USER_FOLLOW_LEVEL)


        # organization
        org = event.org
        if org is not None:
            print "\t\tOrganization [id:", org.id, ']'
            process_organization(org)

        # repository
        """
        repo = event.repo
        if repo is not None:
            print "\t\trepository [id:", repo.id, ';name:', repo.name, ']'
        """ 

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False 


"""
    Process events of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_repoevents(repo):
    try:

        if repo is None:
            return True

        sleep_if_no_rate_remaining()
        events = repo.get_events()

        print "\tEVENTS"
        for event in events:
            process_repoevent(event, repo)

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False 



"""
    Process a GitRelease, crawl its basic info and release version
        ...basic info ...release version
    Parameters:
        release, type of github.GitRelease.GitRelease
    Return:
        status, True if success otherwise False
"""
def process_gitrelease(release):
    try:

        if release is None:
            return True
        
        print "\t\tbody [", release.body, ']'
        print "\t\ttitle [", release.title, ']'
        print "\t\ttag_name", release.tag_name
        print "\t\turl", release.url
        print "\t\tupload_url", release.upload_url
        print "\t\thtml_url", release.html_url
        
        # author type of github.GitAuthor.GitAuthor
        author = release.author

        print "\t\tRELEASEAUTHOR"
        if author is not None:
            process_gitauthor(author)

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False 


"""
    Process assignees of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_repo_assignees(repo):
    try:

        if repo is None:
            return False

        sleep_if_no_rate_remaining()
        assignees = repo.get_assignees()

        for i in range(0, assignees._lenOfFirstPage()):
            assignee = assignees[i]
            process_user(assignee, USER_FOLLOW_LEVEL)

            # assignee-ship
            db_repository_assignee = DB_Repository_Assignee.DB_Repository_Assignee(repo, assignee, conn)
            db_repository_assignee.save()

        page = 0
        while True:
            if assignees._couldGrow() == False:
                break

            assignees_per_page = None
            sleep_if_no_rate_remaining()
            assignees_per_page = assignees._fetchNextPage()

            if assignees_per_page is None:
                continue

            for assignee in assignees_per_page:
                process_user(assignee, USER_FOLLOW_LEVEL)

                # assignee-ship
                db_repository_assignee = DB_Repository_Assignee.DB_Repository_Assignee(repo, assignee, conn)
                db_repository_assignee.save()
            
            print "page", page
            page = page + 1

        """
        print "\tASSIGNEES"
        for assignee in assignees:
            process_user(assignee, USER_FOLLOW_LEVEL)

            # assignee-ship
            db_repository_assignee = DB_Repository_Assignee.DB_Repository_Assignee(repo, assignee, conn)
            db_repository_assignee.save()
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False 


"""
    Process contributors of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_repo_contributors(repo):
    try:

        if repo is None:
            return False

        sleep_if_no_rate_remaining()
        stats_contributors = repo.get_stats_contributors()


        print "\tSTATS CONTRIBUTORS"
        for stats_contributor in stats_contributors:
            contributor = stats_contributor.author
            process_user(contributor, USER_FOLLOW_LEVEL)

            db_repository_contributor = DB_Repository_Contributor.DB_Repository_Contributor(repo, contributor, conn)
            db_repository_contributor.save()

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False 


"""
    Process stargazers of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_repo_stargazers(repo):
    try:

        if repo is None:
            return False

        sleep_if_no_rate_remaining()
        stargazers = repo.get_stargazers()

        print "\tSTARGAZERS"
        for i in range(0, stargazers._lenOfFirstPage()):
            stargazer = stargazers[i]
            process_user(stargazer, USER_FOLLOW_LEVEL)

            db_repository_stargazer = DB_Repository_Stargazer.DB_Repository_Stargazer(repo, stargazer, conn)
            db_repository_stargazer.save()

        while True:
            if stargazers._couldGrow() == False:
                break

            stargazers_per_page = None
            sleep_if_no_rate_remaining()
            stargazers_per_page = stargazers._fetchNextPage()

            if stargazers_per_page is None:
                continue

            for stargazer in stargazers_per_page:
                process_user(stargazer, USER_FOLLOW_LEVEL)

                db_repository_stargazer = DB_Repository_Stargazer.DB_Repository_Stargazer(repo, stargazer, conn)
                db_repository_stargazer.save()
            
        
        """
        print "\tSTARGAZERS"
        for stargazer in stargazers:
            process_user(stargazer, USER_FOLLOW_LEVEL)

            db_repository_stargazer = DB_Repository_Stargazer.DB_Repository_Stargazer(repo, stargazer, conn)
            db_repository_stargazer.save()
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False 


"""
    Process subscribers of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_repo_subscribers(repo):
    try:

        if repo is None:
            return False

        sleep_if_no_rate_remaining()
        subscribers = repo.get_subscribers()

        print "\tSUBSCRIBERS"
        for i in range(0, subscribers._lenOfFirstPage()):
            subscriber = subscribers[i]
            process_user(subscriber, USER_FOLLOW_LEVEL)

            db_repository_subscriber = DB_Repository_Subscriber.DB_Repository_Subscriber(repo, subscriber, conn)
            db_repository_subscriber.save()

        while True:
            if subscribers._couldGrow() == False:
                break

            subscribers_per_page = None
            sleep_if_no_rate_remaining()
            subscribers_per_page = subscribers._fetchNextPage()

            if subscribers_per_page is None:
                continue

            for subscriber in subscribers_per_page:
                process_user(subscriber, USER_FOLLOW_LEVEL)

                db_repository_subscriber = DB_Repository_Subscriber.DB_Repository_Subscriber(repo, subscriber, conn)
                db_repository_subscriber.save()
            
    
        """
        for subscriber in subscribers:
            process_user(subscriber, USER_FOLLOW_LEVEL)

            db_repository_subscriber = DB_Repository_Subscriber.DB_Repository_Subscriber(repo, subscriber, conn)
            db_repository_subscriber.save()
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False 


"""
    Process watchers of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if success otherwise False
"""
def process_repo_watchers(repo):
    try:

        if repo is None:
            return False
        
        sleep_if_no_rate_remaining()
        watchers = repo.get_watchers()

        print "\tWATCHERS"
        for i in range(0, watchers._lenOfFirstPage()):
            watcher = watchers[i]
            process_user(watcher, USER_FOLLOW_LEVEL)

            db_repository_watcher = DB_Repository_Watcher.DB_Repository_Watcher(repo, watcher, conn)
            db_repository_watcher.save()

        page = 0
        while True:
            if watchers._couldGrow() == False:
                break

            watchers_per_page = None
            sleep_if_no_rate_remaining()
            watchers_per_page = watchers._fetchNextPage()

            if watchers_per_page is None:
                continue

            for watcher in watchers_per_page:
                process_user(watcher, USER_FOLLOW_LEVEL)

                db_repository_watcher = DB_Repository_Watcher.DB_Repository_Watcher(repo, watcher, conn)
                db_repository_watcher.save()
            
        
        """
        print "\tWATCHERS"
        for watcher in watchers:
            process_user(watcher, USER_FOLLOW_LEVEL)

            db_repository_watcher = DB_Repository_Watcher.DB_Repository_Watcher(repo, watcher, conn)
            db_repository_watcher.save()
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False 


"""
    Process languages of one repository
    Parameters:
        repo, type of github.Repository.Repository
    Return:
        status, True if suceess otherwise False
"""
def process_repo_languages(repo):
    try:

        if repo is None:
            return False

        if open_if_connection_closed() == False:
            return False

        sleep_if_no_rate_remaining()
        langs = repo.get_languages()

        print "\tlanguages: ", langs

        db_repository_languages = DB_Repository_Languages.DB_Repository_Languages(langs, repo, conn)
        db_repository_languages.save()

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False 



"""
    Process a repository, for each repository, crawl its basic info and relationship info
        first, crawl its related users
        ...
    Parameters: type of github.Repository.Repository
    Return:  status, True if success otherwise False
"""
def process_repo(repo):
    try:

        print 'Repository ', '[id:', repo.id, '; name:', repo.name, ']'
        
        if open_if_connection_closed() == False:
            return False

        db_repo = DB_Repository.DB_Repository(repo, conn)

        if db_repo.exist():
            return True

        db_repo.save()        


        # archive_link
        sleep_if_no_rate_remaining()
        archive_link = repo.get_archive_link("zipball")

        print 'downloading', archive_link, '...'
        archive_local_url = wget_upload_clean(archive_link, ".zip")
        print archive_local_url
        if archive_local_url is not None:
            db_repo.update_one("archive_local_url", archive_local_url)          
       


        """
            First, crawl its related users which includes OWNER, COLLABORATORS, ASSIGNEES, CONTRIBUTORS, STARGAZERS, SUBSCRIBERS, WATCHERS
        """
        
        # OWNER
        owner = repo.owner
        
        print "\tOWNER"
        process_user(owner, USER_FOLLOW_LEVEL)


        # COLLABORATORS (require the current user must be an authorized user)
        #sleep_if_no_rate_remaining()
        #collaborators = repo.get_collaborators()

        #print "\tCOLLABORATORS"
        #for collaborator in collaborators:
        #    process_user(collaborator, USER_FOLLOW_LEVEL)

        # ASSIGNEES
        process_repo_assignees(repo)


        # STAT CONTRIBUTORS
        process_repo_contributors(repo)

        
        # STARGAZERS
        process_repo_stargazers(repo)
        

        # SUBSCRIBERS
        process_repo_subscribers(repo)

      
        # WATCHERS
        process_repo_watchers(repo)


        # commits
        process_commits(repo)


        # branches (placed behind 'commits' section)
        process_branches(repo)
        
        
        # labels
        process_repo_labels(repo)       

        
        # languages
        process_repo_languages(repo)        

        
        # milestones
        process_milestones(repo)


        # issues
        process_issues(repo)     


        # pulls
        process_pulls(repo)
        
        
        # README
        process_readme(repo)        
        

        # TAGS (RELEASE VERSION TAGs)
        process_tags(repo)

        

        # TEAMS (requirement is an authorized user that has access rights)



        # KEYS GitHubException {
        #    "u'documentation_url': u'https://developer.github.com/v3', u'message': u'Not Found'"
        # }
        #sleep_if_no_rate_remaining()
        #keys = repo.get_keys()
        #
        #print "\tKEYS"
        #for key in keys:
        #    process_key(key)


        # FORKS (not now, maybe TODO)

        
        # ORGANIZATION
        org = repo.organization
        if org is not None:
            print "\tORGANIZATION"
            process_organization(org)


        # REPO EVENTS (the latest 90 days, at most 300 events)
        process_repoevents(repo)
        


        # RELEASES
        #sleep_if_no_rate_remaining()
        #releases = repo.get_releases()
        #
        #sleep_if_no_rate_remaining()
        #print "total releases", releases.totalCount
        #
        #print "\tRELEASES"
        #for release in releases:
        #    process_gitrelease(release)

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False





"""
    Process a set of repositories
    Parameters: type of github.PaginatedList.PaginatedList of github.Repository.Repository
    Return: status, True if success otherwise False
"""
def process_repos(repos):
    try:


        for i in range(0, repos._lenOfFirstPage()):
            repo = repos[i]
            # for each repository
            print repo.id, repo.name, repo.stargazers_count

            process_repo(repo)


        while True:
            if repos._couldGrow() == False:
                break

            repos_per_page = None
            sleep_if_no_rate_remaining()
            repos_per_page = repos._fetchNextPage()

            if repos_per_page is None:
                continue

            if len(repos_per_page) == 0:
                break

            for repo in repos_per_page:            
                # for each repository
                print repo.id, repo.name, repo.stargazers_count

                process_repo(repo)

        """
        for repo in repos:
            # for each repository
            print repo.id, repo.name, repo.stargazers_count

            process_repo(repo)

            #status = process_repo(repo)
            #if status ==  False:
            #    return False
        """
        
        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
    except Exception, e:
        print e


"""
    Search 1000 reporitories with the most stars and require their main language must be the specified one
    Parameters:
        lang, program language, type of basestring
    Return:
        status, True if success otherwise False
"""
def search_repositories_first(lang):
    
    global last_stars

    try:

        sleep_if_no_rate_remaining()
        repos = g.search_repositories('', 'stars', 'desc', language=lang, stars="<"+str(last_stars))

        i = 0
        for j in range(0, repos._lenOfFirstPage()):
            repo = repos[j]
            print repo.id, repo.name, repo.stargazers_count, i
            
            process_repo(repo)
            # TODO if needed to add check for err loop
            last_stars = repo.stargazers_count
            i = i + 1


        while True:
            if repos._couldGrow() == False:
                break

            repos_per_page = None
            sleep_if_no_rate_remaining()
            repos_per_page = repos._fetchNextPage()

            if repos_per_page is None:
                continue

            if len(repos_per_page) == 0:
                break

            for repo in repos_per_page:
                print repo.id, repo.name, repo.stargazers_count, i
            
                process_repo(repo)
                # TODO if needed to add check for err loop
                last_stars = repo.stargazers_count
                i = i + 1
            

        """
        i = 0
        for repo in repos:
            print repo.id, repo.name, repo.stargazers_count, i
            
            process_repo(repo)
            # TODO if needed to add check for err loop
            last_stars = repo.stargazers_count
            i = i + 1
        """

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    search by each star until the total count of returned repositories greater than 1000
    Parameters:
        lang, main program language, type of basestring
    Return:
        status, True if success otherwise False
"""
def search_repositories_second(lang):

    global last_stars

    try:

        while True:

            sleep_if_no_rate_remaining()
            repos = g.search_repositories('','forks', 'desc', language=lang, stars=last_stars)
        
            sleep_if_no_rate_remaining()
            totalCount = repos.totalCount

            print last_stars, totalCount

            if totalCount > 1000 or last_stars < 0:
                break

            process_repos(repos)

            last_stars = last_stars - 1

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


"""
    Search repositories of one specified language and stars in a week day by day
    Parameters:
        lang, main program language, type of basestring
        end_date_week, end of the specified week, type of datetime.date
    Return:
        status, True if success otherwise False
"""
def search_repositories_third_day(lang, end_date_week):

    global last_stars, start_date_day

    try:

        while start_date_day <= end_date_week:
            end_date_day = start_date_day

            sleep_if_no_rate_remaining()
            repos = g.search_repositories('', 'forks', 'desc', stars=last_stars, language=lang, created=str(start_date_day) + '..' + str(end_date_day))

            sleep_if_no_rate_remaining()
            totalCount =repos.totalCount
            print '\t\tday', last_stars, str(start_date_day), str(end_date_day), totalCount

            if totalCount > 1000:
                print "\t\t\tday >1000"

            process_repos(repos)
                        
            start_date_day = end_date_day + datetime.timedelta(days=1)                                

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Search repositories of specified language and stars in a specified month week by week
    Parameters:
        lang, main program language, type of basestring
        end_date, end of the specified month, type of datetime.date
    Return:
        status, True if success otherwise False
"""
def search_repositories_third_week(lang, end_date):

    global last_stars, start_date_week, start_date_day

    try:

        while start_date_week <= end_date:
            end_date_week = start_date_week + datetime.timedelta(days=6)
            end_date_week = end_date_week if end_date_week < end_date else end_date

            sleep_if_no_rate_remaining()
            repos = g.search_repositories('', 'forks', 'desc', stars=last_stars, language=lang, created=str(start_date_week) + '..' + str(end_date_week))

            sleep_if_no_rate_remaining()
            totalCount = repos.totalCount
            print '\tweek', last_stars, str(start_date_week), str(end_date_week), totalCount

            if totalCount > 1000:
                print "\tweek > 1000"

                start_date_day = start_date_week
                while True:
                    if search_repositories_third_day(lang, end_date_week):
                        break
            else:
                process_repos(repos)

            start_date_week = end_date_week + datetime.timedelta(days=1)                

        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False



"""
    Search repositories of specified language and stars by date (month by month)
    Parameters:
        lang, program language, type of basestring
    Return:
        status, True if success otherwise False
"""
def search_repositories_third_month(lang):

    global last_stars, start_date, start_date_week

    try:

        while start_date <= datetime.date.today():

            days = 31 if start_date.month in [1,3, 5, 7 ,8 ,10, 12] else 30 if start_date.month != 2 else 29 if start_date.year % 4 == 0 else 28
            end_date = start_date + datetime.timedelta(days=(days - 1))
            sleep_if_no_rate_remaining()
            repos = g.search_repositories('', 'forks', 'desc', stars=last_stars, language=lang, created=str(start_date) + '..' + str(end_date))

            sleep_if_no_rate_remaining()
            totalCount = repos.totalCount
            print 'month', last_stars, str(start_date), str(end_date), totalCount

            if totalCount > 1000:
                    
                print "month >1000", totalCount
                    
                start_date_week = start_date
                while True:
                    if search_repositories_third_week(lang, end_date):
                        break

            else:
                process_repos(repos)

            start_date = end_date + datetime.timedelta(days=1)
               
        return True

    except github.GithubException as ge:
        print "GithubException", ge.status, ge.data
        return False
    except github.BadAttributeException as bae:
        print "BadAttributeException", bae.actualValue, bae.exceptedType, bae.transformException
        return False
    except Exception, e:
        print e
        return False


if __name__ == "__main__":

    lang = 'C'

    """
        Search all repositories:
            first, search 1000 reporitories with the most stars and require their main language must be the specified one
    """
    
    while True:
        if search_repositories_first(lang) == True:
            break
    
    print 'last_stars', last_stars

    """
        second, search by each star until the total count of returned repositories greater than 1000
    """
    while True:    
        if search_repositories_second(lang) == True:
            break
    

    """
        third, search by each stars; for each stars, search by created date which is splitted into months, weeks and even days if necessary
    """
    while last_stars >= 0:

        #for each stars, find 
        start_date = datetime.date(2008, 1, 1)
        if search_repositories_third_month(lang) == True:
        
            last_stars = last_stars - 1
