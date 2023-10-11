from pydantic import BaseModel
from abc import ABC, abstractmethod
from collections import defaultdict


class PublicModel(ABC):
    @abstractmethod
    def book_info(self):
        pass


class BookModel(BaseModel):
    title: str
    author: str
    year: int


class MagazineModel(BaseModel):
    title: str
    author: str
    year: int


class Book(PublicModel):
    def __init__(self, book_model: BookModel):
        self.title = book_model.title
        self.author = book_model.author
        self.year = book_model.year

    def book_info(self):  # Implementing the abstract method
        return f"{self.title}, Автор: {self.author}, Рік видання: {self.year}"

    def __eq__(self, other):
        if not isinstance(other, Book):
            return False
        return (self.title, self.author, self.year) == (other.title, other.author, other.year)

    def __hash__(self):
        return hash((self.title, self.author, self.year))


class Magazine(PublicModel):
    def __init__(self, magazine_model: MagazineModel):
        self.title = magazine_model.title
        self.author = magazine_model.author
        self.year = magazine_model.year

    def book_info(self):  # Implementing the abstract method
        return f"{self.title}, Автор: {self.author}, Рік видання: {self.year}"

    def __eq__(self, other):
        if not isinstance(other, Magazine):
            return False
        return (self.title, self.author, self.year) == (other.title, other.author, other.year)

    def __hash__(self):
        return hash((self.title, self.author, self.year))


def log_addition(func):
    def wrapper(self, book_model):
        if isinstance(book_model, BookModel):
            print(f"Додаємо: {book_model.title} (Автор: {book_model.author})")
        elif isinstance(book_model, MagazineModel):
            print(f"Додаємо: {book_model.title} (Автор: {book_model.author})")
        return func(self, book_model)
    return wrapper


def check_book_existence(func):
    def wrapper(*args, **kwargs):
        library, _book = args[0], args[1]
        if _book in library.books:
            removed_book = func(*args, **kwargs)
            if removed_book:
                print(f"\nВидаленo: {removed_book}")
                return removed_book  # Returning the removal result
        else:
            print(f"\nКнига не знайдена у бібліотеці.")
            return None  # Returning None if the book was not found
    return wrapper


class Library:
    def __init__(self):
        self.books = set()
        self.books_by_author_dict = defaultdict(list)  # Author: [list of books]
        print("Бібліотека створена\n")

    @log_addition
    def add_book(self, book_model: BookModel):
        book = Book(book_model)
        if book not in self.books:
            self.books.add(book)
            self.books_by_author_dict[book.author].append(book)

    @log_addition
    def add_magazine(self, magazine_model: MagazineModel):
        existing_magazine = next((book for book in self.books if book.title == magazine_model.title and isinstance(book, Magazine)), None)
        if existing_magazine:
            print(f"Журнал {magazine_model.title} вже є у бібліотеці.")
            return
        magazine = Magazine(magazine_model)
        if magazine not in self.books:
            self.books.add(magazine)
            self.books_by_author_dict[magazine.author].append(magazine)

    @staticmethod
    def print_books_by_author(author_name, books_by_author_dict):
        if author_name in books_by_author_dict:
            books = books_by_author_dict[author_name]
            for book in books:
                print(book.book_info())
        else:
            print(f"Книги автора {author_name} не знайдено.")

    @check_book_existence
    def remove_book(self, book_to_remove):
        if book_to_remove in self.books:
            self.books.remove(book_to_remove)
            self.books_by_author_dict[book_to_remove.author].remove(book_to_remove)
            return book_to_remove.book_info()
        else:
            return None

    def __iter__(self):
        return iter(self.books)

    # Generator that returns books by author name
    def books_by_author(self, author_name):
        for book in self.books:
            if book.author == author_name:
                yield book


class FileManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def __enter__(self):
        return open(self.file_path, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


if __name__ == "__main__":
    library: Library = Library()

    book_model1 = BookModel(title="Книга: Магия утра", author="Хэл Элрод", year=2014)
    book_model2 = BookModel(title="Книга: Эссенциализм", author="Грег МакКеон", year=2014)
    book_model3 = BookModel(title="Книга: Магическая формула", author="Хэл Элрод", year=2019)
    journal_model1 = MagazineModel(title="Журнал: The Ukrainian Week", author="Ukraine", year=2019)

    book1 = Book(book_model1)
    book2 = Book(book_model2)
    book3 = Book(book_model3)
    journal1 = Magazine(journal_model1)

    library.add_book(book_model1)
    library.add_book(book_model2)
    library.add_book(book_model3)
    library.add_magazine(journal_model1)

    print("\nСписок книг у бібліотеці:")
    for item in library:
        print(item.book_info())

    print("\nСписок книг у бібліотеці за автором Хэл Элрод:")
    library.print_books_by_author("Хэл Элрод", library.books_by_author_dict)

    with FileManager("books.txt") as file:
        for item in library:
            file.write(f"{item.title}, {item.author}, {item.year}\n")

    removed_book_info = library.remove_book(book1)

    print("\nСписок у бібліотеці після видалення:")
    for item in library:
        print(item.book_info())

    print("\nДодавання книг з файлу в бібліотеку:")
    with open("books.txt", 'r') as file:
        lines = file.readlines()
        for line in lines:
            book_info = line.strip().split(", ")
            book_model = BookModel(title=book_info[0], author=book_info[1], year=int(book_info[2]))
            library.add_book(book_model)

    print("\nСписок у бібліотеці після додавання з файлу:")
    for item in library:
        print(item.book_info())
