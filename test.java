public static void main(){
    public int countoccurence(int num, int digitToFind){
        //num = 121
        //convert the number to string
        //"121"
        //convert digit to find to string
        // "1"
        //loop through the string and count the occurrences of the digit in string
        //return the count
        String numToString = Integer.toString(num);
        String digitToString = Integer.toString(digitToFind);
        int counter = 0;
        for(int i = 0; i<numToString; i++){
            if (numToString[i] == digitToString[i]){
                counter++;
            }
        }
        return counter;
    }

    countoccurence(1,121)
}