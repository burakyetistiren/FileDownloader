
# FileDownloader

# Description
Program in Python downloads an index file to obtain a list of text file URLs and download some of these files depending on their sizes. No HTTP client libraries, or the HTTP specific core or non-core APIs are used, instead, the Socket package in Python is used.


# Command
    FileDownloader <index_file> [<lower_endpoint>-<upper_endpoint>]


where \<indexfile> and \<lowerendpoint>-\<upperendpoint> are
the command-line arguments. The details of the command-line arguments are as follows:

-   \<index_file>: [Required] The URL of the index that includes a list of text file URLs.
    
-   \<lower_endpoint>-\<upper_endpoint>: [Optional] If this argument is not given, a file in the index is downloaded if it is found in the index. Otherwise, the bytes between \<lower_endpoint> and \<upper_endpoint> inclusively are to be downloaded.

# Details
When a user enters the command above, the program sends an HTTP GET request to the server in order to download the index file with URL \<index_file>. If the index file is not found, the response is a message other than 200 OK. In this case, program prints an error message to the command-line and exits. If the index file is found, the response is a 200 OK message. When this is the case, program prints the number of file URLs in the index file and sends an HTTP HEAD request for each file URL in the index file.

**Requested file is not found:** If the requested file is not found in the server, the response is a message other than 200 OK. In this case, program prints a message to the command-line indicating that the file is not found. Then, an HTTP HEAD request is sent for the next file.

**Requested file is found:** If the requested file is found in the server, the response is a 200 OK message which includes the size of the file in bytes in the header. When this is the case, there are these possibilities:

1.  If the user does not give a range as a command-line argument, program sends an HTTP GET message to obtain the content of the whole file.
    
2.  If a range is given as a command-line argument and the size of the file is smaller than \<lower_endpoint>, the file will not be downloaded and program prints a message to the command-line indicating that the file is not requested. Then, an HTTP HEAD request is sent for the next file.
    
3.  If a range is given as a command-line argument and the size of the file is not smaller than \<lower_endpoint>, the range is satisfiable. Then, program sends an HTTP GET message with the range \<lower_endpoint>-\<upper_endpoint> and obtains a part of the file content from the HTTP 206 Partial Content response.
    
4.  If program successfully obtains the file or a part of the file, it saves the content under the directory in which the program runs. The name of the saved file is the same as the downloaded file and a message indicating that the file is successfully downloaded is printed to the command-line. Then an HTTP HEAD request is sent for the next file.

# Examples
Let www.foo.com/abc/index.txt be the URL of the file to be downloaded whose content is given as:

    www.cs.bilkent.edu.tr/file.txt 
    www.cs.bilkent.edu.tr/folder2/temp.txt 
    wordpress.org/plugins/about/readme.txt 
    humanstxt.org/humans.txt 
    www.cs.bilkent.edu.tr/cs421/deneme.txt

where the first file does not exist in the server and the sizes of the other files are 6000, 4567, 1587, and 9000 bytes, respectively.

**Example run 1.** Let the program start with the FileDownloader
    
    www.foo.com/abc/index.txt

command. Then all files except the first one in the index file are downloaded. After the connection is terminated, the command-line of the client may be as follows:

    Command-line:  
    URL of the index file: www.foo.com/abc/index.txt  
    Lower endpoint = 0  
    Upper endpoint = 999  
    Index file is downloaded  
    There are 5 files in the index  
    1. www.cs.bilkent.edu.tr/file.txt is not found  
    2. www.cs.bilkent.edu.tr/folder2/temp.txt (range = 0-999) is downloaded 
    3. wordpress.org/plugins/about/readme.txt (range = 0-999) is downloaded 
    4. humanstxt.org/humans.txt (range = 0-999) is downloaded  
    5. www.cs.bilkent.edu.tr/cs421/deneme.txt (range = 0-999) is downloaded

**Example run 2.** Let the program start with the FileDownloader

    www.foo.com/abc/index.txt 0-999 

command. Then the first 1000 bytes of all files except the first one in the index file www.foo.com/abc/index.txt are downloaded. After the connection is terminated, the command-line of the client may be as follows:

    Command-line:  
    URL of the index file: www.foo.com/abc/index.txt  
    Lower endpoint = 0  
    Upper endpoint = 999  
    Index file is downloaded  
    There are 5 files in the index  
    1. www.cs.bilkent.edu.tr/file.txt is not found  
    2. www.cs.bilkent.edu.tr/folder2/temp.txt (range = 0-999) is downloaded 
    3. wordpress.org/plugins/about/readme.txt (range = 0-999) is downloaded 
    4. humanstxt.org/humans.txt (range = 0-999) is downloaded  
    5. www.cs.bilkent.edu.tr /cs421/deneme.txt (range = 0-999) is downloaded

**Example run 3.** Let the program start with the FileDownloader

    www.foo.com/abc/index.txt 1587-6999

command. The last byte of the fourth file is 1586, so it is not requested. Hence, the bytes in the range 1587-6999 are requested for the second, third, and fifth files. Since the second and third files do not include 7000 bytes, the response includes the bytes in the ranges 1587-5999 and 1587-4566, respectively. After the connection is terminated, the command-line of the client may be as follows:

    Command-line:  
    URL of the index file: www.foo.com/abc/index.txt  
    Lower endpoint = 1587  
    Upper endpoint = 6999  
    Index file is downloaded  
    There are 5 files in the index  
    1. www.cs.bilkent.edu.tr/file.txt is not found  
    2. www.cs.bilkent.edu.tr/folder2/temp.txt (range = 1587-5999) is downloaded 
    3. wordpress.org/plugins/about/readme.txt (range = 1587-4566) is downloaded 
    4. humanstxt.org/humans.txt (size = 1587) is not downloaded  
    5. www.cs.bilkent.edu.tr/ cs421/deneme.txt (range = 1587-6999) is downloaded
