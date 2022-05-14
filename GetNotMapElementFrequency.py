import os
import glob

# 得到没有进行映射的元素出现的频率
def remainingElementFrequency(filePath):
    filePathList = os.listdir(filePath);
    for i in filePathList:
        fileList = os.path.join(filePath,i);
        fileList = glob.glob(os.path.join(fileList, '*'))
        for file in fileList:
            ApkName = os.path.splitext(file)[0]  # 将txt文件按照它们的文件名和后缀做一个分割
            ApkName = ApkName.split("/")[-1]
            f = open(file)
            contents = f.readlines()
            length = 0;
            ele_per = 0;
            ele_and = 0;
            for msg in contents:
                msg = msg.strip('\n')
                length =  length + len(msg)
                ele_and = ele_and + msg.count('&')
                ele_per = ele_per + msg.count('%')
            print(ApkName + ": The frequency of '%' is ",float('%.4f' %(ele_per/length)))
            print(ApkName + ": The frequency of '&' is ",float('%.4f' %(ele_and/length)))

