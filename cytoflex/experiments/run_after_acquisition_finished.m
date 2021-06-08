%% Remove and replace experiment files

cd C:\my_git_repo\evotron\cytoflex\experiments

delete([pwd filesep 'cyto_expt_file.xit']);
delete([pwd filesep '\cyto_expt_file\01-Well-A1.fcs']);
copyfile([pwd filesep '\sample_experiments\cyto_expt_file.xit'], 'cyto_expt_file.xit') 
copyfile([pwd filesep '\sample_experiments\01-Well-A1.fcs'], [pwd filesep '\cyto_expt_file\01-Well-A1.fcs']);
