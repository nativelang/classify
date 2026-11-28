import io.nativelang.classify.Classifier;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Arrays;

public class Movie {
    public static void main(String[] args) throws Exception {
        var input = new BufferedReader(new InputStreamReader(System.in));
        try (var model = new Classifier()) {
            System.out.println(System.getProperty("os.arch"));
            for (String line; (line = input.readLine()) != null;) {
                String[] fields = line.split("\t");
                String label = model.classify(fields[0], Arrays.copyOfRange(fields, 1, fields.length));
                System.out.println(label == null ? "" : label);
            }
        }
    }
}
