function [] = save_acquisition_files(evolverExptDir, cytoTemplateDir, vialNum, count)
%% Save acquisition files and prepare for next cytoflex acquisition

    vialNum = erase(vialNum, ["!" "?"]);

    % delete .xit file for next acquisition
    delete('C:\my_git_repo\evotron\cytoflex\experiments\cyto_expt_file.xit');
    
    % copy output .fcs file to results directory and delete it
    copyfile('C:\my_git_repo\evotron\cytoflex\experiments\cyto_expt_file\01-Well-A1.fcs', ...
        strcat(evolverExptDir, '\sampling_results\fcs_output\vial_', vialNum, '_sample_', num2str(count), '.fcs'));
    delete('C:\my_git_repo\evotron\cytoflex\experiments\cyto_expt_file\01-Well-A1.fcs');
    
    % copy acquisition result .xml file to the results directory and delete it
    copyfile('C:\my_git_repo\evotron\cytoflex\experiments\acquisition_result.xml', ...
        strcat(evolverExptDir, '\sampling_results\vial_', vialNum, '_acquisition_result_', num2str(count), '.xml'));
    delete('C:\my_git_repo\evotron\cytoflex\experiments\acquisition_result.xml');

    % copy original template files to the cytoflex experiment directory
    copyfile(strcat(cytoTemplateDir, '\cyto_expt_file.xit'), ...
        'C:\my_git_repo\evotron\cytoflex\experiments\cyto_expt_file.xit');    
    copyfile(strcat(cytoTemplateDir, '\01-Well-A1.fcs'), ...
        'C:\my_git_repo\evotron\cytoflex\experiments\cyto_expt_file\01-Well-A1.fcs');
    
end
