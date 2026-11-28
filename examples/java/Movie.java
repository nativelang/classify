import io.nativelang.classify.Classifier;

class Movie {
    public static void main(String[] args) throws Exception {
        try (var model = new Classifier()) {
            String category = model.classify("This is a terrible movie", "positive", "negative", "neutral");
            System.out.println(category == null ? "unknown" : category);
        }
    }
}
