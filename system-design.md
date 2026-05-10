# Java Software Architect — Comprehensive Interview Preparation Guide

> **Target Audience:** Senior Java Developers (10+ years) preparing for Software Architect interviews
> **Last Updated:** May 2026

---

## Table of Contents

- [Part I: Java Design Patterns](#part-i-java-design-patterns)
  - [1. Creational Patterns](#1-creational-patterns)
  - [2. Structural Patterns](#2-structural-patterns)
  - [3. Behavioral Patterns](#3-behavioral-patterns)
  - [4. Concurrency Patterns](#4-concurrency-patterns)
  - [5. Architectural Patterns](#5-architectural-patterns)
- [Part II: Microservices Design Patterns](#part-ii-microservices-design-patterns)
- [Part III: System Design](#part-iii-system-design)
- [Part IV: Company-Wise Interview Questions & Answers](#part-iv-company-wise-interview-questions--answers)
- [Part V: Interview Tips & Strategies](#part-v-interview-tips--strategies)

---

# Part I: Java Design Patterns

Design patterns are proven solutions to recurring problems in software design. For a Java architect, understanding these patterns deeply — including their trade-offs, when to apply them, and when NOT to — is critical. This section covers all 23 GoF (Gang of Four) patterns, plus essential concurrency and architectural patterns every architect must know.

## 1. Creational Patterns

Creational patterns deal with object creation mechanisms, providing flexibility in what is created, who creates it, and how and when it is created.

---

### 1.1 Singleton Pattern

**Intent:** Ensure a class has only one instance and provide a global point of access to it.

**When to Use:**
- Logging frameworks, configuration managers, connection pools, thread pools
- When exactly one object is needed to coordinate actions across the system

**When NOT to Use:**
- When you need multiple instances (obviously)
- In distributed systems where you need one instance per JVM
- When it introduces hidden global state that makes testing difficult

**Diagram:**
```
┌─────────────────────────────┐
│        Singleton            │
├─────────────────────────────┤
│ - instance: Singleton       │
├─────────────────────────────┤
│ - Singleton()               │
│ + getInstance(): Singleton  │
└─────────────────────────────┘
         │
         ▼
   Only one instance exists
```

**Implementation — Eager Initialization:**
```java
public class EagerSingleton {
    // Created at class loading time
    private static final EagerSingleton instance = new EagerSingleton();

    private EagerSingleton() {
        // Prevent reflection attack
        if (instance != null) {
            throw new IllegalStateException("Singleton already initialized");
        }
    }

    public static EagerSingleton getInstance() {
        return instance;
    }
}
```

**Implementation — Double-Checked Locking (Lazy + Thread-Safe):**
```java
public class DoubleCheckedLockingSingleton {
    // volatile prevents partial construction visibility
    private static volatile DoubleCheckedLockingSingleton instance;

    private DoubleCheckedLockingSingleton() {}

    public static DoubleCheckedLockingSingleton getInstance() {
        if (instance == null) {                    // First check (no locking)
            synchronized (DoubleCheckedLockingSingleton.class) {
                if (instance == null) {            // Second check (with locking)
                    instance = new DoubleCheckedLockingSingleton();
                }
            }
        }
        return instance;
    }
}
```

**Implementation — Bill Pugh (Inner Static Helper — Most Recommended):**
```java
public class BillPughSingleton {
    private BillPughSingleton() {}

    // Inner static helper class is not loaded until getInstance() is called
    private static class SingletonHelper {
        private static final BillPughSingleton INSTANCE = new BillPughSingleton();
    }

    public static BillPughSingleton getInstance() {
        return SingletonHelper.INSTANCE;
    }
}
```

**Implementation — Enum Singleton (Best for Serialization Safety):**
```java
public enum EnumSingleton {
    INSTANCE;

    private AtomicInteger counter = new AtomicInteger(0);

    public int increment() {
        return counter.incrementAndGet();
    }
}

// Usage: EnumSingleton.INSTANCE.increment();
```

**Common Interview Trap — Breaking Singleton:**
```java
// 1. Reflection attack
Constructor<BillPughSingleton> constructor =
    BillPughSingleton.class.getDeclaredConstructor();
constructor.setAccessible(true);
BillPughSingleton broken = constructor.newInstance(); // Creates new instance!

// 2. Serialization attack
// If singleton implements Serializable, deserialization creates new instance
// Fix: implement readResolve()
protected Object readResolve() {
    return getInstance();
}

// 3. Cloning attack
// If singleton extends Cloneable class
// Fix: throw CloneNotSupportedException in clone()
@Override
protected Object clone() throws CloneNotSupportedException {
    throw new CloneNotSupportedException("Singleton cannot be cloned");
}
```

**Interview Q:** *Why is `volatile` needed in double-checked locking?*
**A:** Without `volatile`, the JVM may reorder instructions such that a thread sees a non-null reference to a partially constructed object. The `volatile` keyword establishes a happens-before relationship, ensuring the object is fully constructed before its reference becomes visible.

---

### 1.2 Factory Method Pattern

**Intent:** Define an interface for creating objects, but let subclasses decide which class to instantiate. Factory Method lets a class defer instantiation to subclasses.

**When to Use:**
- When a class cannot anticipate the class of objects it must create
- When you want to localize object creation logic
- When you need to provide a library/framework that creates objects without specifying their concrete classes

**Diagram:**
```
┌──────────────────┐          ┌──────────────────┐
│   Creator        │          │   Product        │
├──────────────────┤          ├──────────────────┤
│ + factoryMethod()│◄─────────│ + operation()    │
│ + anOperation()  │          └──────────────────┘
└────────┬─────────┘                  ▲
         │                            │
    ┌────┴─────┐              ┌───────┴───────┐
    │          │              │               │
┌───┴────┐ ┌──┴─────┐  ┌────┴─────┐  ┌──────┴────┐
│Concrete│ │Concrete│  │Concrete  │  │Concrete   │
│CreatorA│ │CreatorB│  │ProductA  │  │ProductB   │
└────────┘ └────────┘  └──────────┘  └───────────┘
```

**Implementation:**
```java
// Product interface
public interface Notification {
    void send(String message);
}

// Concrete Products
public class EmailNotification implements Notification {
    @Override
    public void send(String message) {
        System.out.println("Sending Email: " + message);
    }
}

public class SMSNotification implements Notification {
    @Override
    public void send(String message) {
        System.out.println("Sending SMS: " + message);
    }
}

public class PushNotification implements Notification {
    @Override
    public void send(String message) {
        System.out.println("Sending Push: " + message);
    }
}

// Creator
public abstract class NotificationFactory {
    public abstract Notification createNotification();

    // Business logic that uses the product
    public void notifyUser(String message) {
        Notification notification = createNotification();
        notification.send(message);
    }
}

// Concrete Creators
public class EmailNotificationFactory extends NotificationFactory {
    @Override
    public Notification createNotification() {
        return new EmailNotification();
    }
}

public class SMSNotificationFactory extends NotificationFactory {
    @Override
    public Notification createNotification() {
        return new SMSNotification();
    }
}
```

**Spring Framework Real-World Example:**
```java
// Spring's FactoryBean is a Factory Method implementation
public class DataSourceFactoryBean implements FactoryBean<DataSource> {
    private String driverClassName;
    private String url;
    private String username;
    private String password;

    @Override
    public DataSource getObject() {
        HikariDataSource ds = new HikariDataSource();
        ds.setDriverClassName(driverClassName);
        ds.setJdbcUrl(url);
        ds.setUsername(username);
        ds.setPassword(password);
        return ds;
    }

    @Override
    public Class<?> getObjectType() {
        return DataSource.class;
    }
}
```

---

### 1.3 Abstract Factory Pattern

**Intent:** Provide an interface for creating families of related or dependent objects without specifying their concrete classes.

**When to Use:**
- When the system needs to be independent of how its products are created
- When you need to create families of related objects (e.g., UI themes, cross-platform widgets)
- When you want to provide a product library that reveals only interfaces, not implementations

**Diagram:**
```
┌─────────────────────┐
│  AbstractFactory    │
├─────────────────────┤
│ + createProductA()  │
│ + createProductB()  │
└─────────┬───────────┘
          │
    ┌─────┴──────┐
    │            │
┌───┴──────┐ ┌──┴───────┐
│Concrete  │ │Concrete   │
│Factory1  │ │Factory2   │
└──┬───┬───┘ └──┬───┬───┘
   │   │        │   │
   ▼   ▼        ▼   ▼
  P1A P1B      P2A P2B
```

**Implementation:**
```java
// Abstract Products
public interface Button { void render(); }
public interface TextField { void display(); }

// Mac Family
public class MacButton implements Button {
    @Override
    public void render() { System.out.println("Mac-style button"); }
}
public class MacTextField implements TextField {
    @Override
    public void display() { System.out.println("Mac-style text field"); }
}

// Windows Family
public class WindowsButton implements Button {
    @Override
    public void render() { System.out.println("Windows-style button"); }
}
public class WindowsTextField implements TextField {
    @Override
    public void display() { System.out.println("Windows-style text field"); }
}

// Abstract Factory
public interface UIFactory {
    Button createButton();
    TextField createTextField();
}

// Concrete Factories
public class MacUIFactory implements UIFactory {
    @Override
    public Button createButton() { return new MacButton(); }
    @Override
    public TextField createTextField() { return new MacTextField(); }
}

public class WindowsUIFactory implements UIFactory {
    @Override
    public Button createButton() { return new WindowsButton(); }
    @Override
    public TextField createTextField() { return new WindowsTextField(); }
}

// Client
public class Application {
    private Button button;
    private TextField textField;

    public Application(UIFactory factory) {
        this.button = factory.createButton();
        this.textField = factory.createTextField();
    }

    public void renderUI() {
        button.render();
        textField.display();
    }
}
```

**Interview Q:** *What is the difference between Factory Method and Abstract Factory?*
**A:** Factory Method creates one product through inheritance (subclass decides), while Abstract Factory creates families of related products through composition (factory object decides). Abstract Factory often uses Factory Methods internally.

---

### 1.4 Builder Pattern

**Intent:** Separate the construction of a complex object from its representation so that the same construction process can create different representations.

**When to Use:**
- When an object has many optional parameters or configuration options
- When you want immutable objects with many attributes
- When the constructor telescoping problem occurs

**Diagram:**
```
┌─────────────┐    ┌──────────────────┐
│  Director   │───►│   Builder        │
├─────────────┤    ├──────────────────┤
│+ construct()│    │+ buildPartA()    │
└─────────────┘    │+ buildPartB()    │
                   │+ getResult()     │
                   └────────┬─────────┘
                            │
                     ┌──────┴───────┐
                     │              │
              ┌──────┴───┐   ┌─────┴──────┐
              │Concrete  │   │Concrete    │
              │Builder1  │   │Builder2    │
              └──────────┘   └────────────┘
```

**Implementation:**
```java
public class HttpRequest {
    private final String method;
    private final String url;
    private final Map<String, String> headers;
    private final String body;
    private final int timeout;
    private final boolean followRedirects;

    private HttpRequest(Builder builder) {
        this.method = builder.method;
        this.url = builder.url;
        this.headers = Collections.unmodifiableMap(builder.headers);
        this.body = builder.body;
        this.timeout = builder.timeout;
        this.followRedirects = builder.followRedirects;
    }

    // Builder class
    public static class Builder {
        // Required parameters
        private final String method;
        private final String url;

        // Optional parameters with defaults
        private Map<String, String> headers = new HashMap<>();
        private String body = "";
        private int timeout = 30000;
        private boolean followRedirects = true;

        public Builder(String method, String url) {
            this.method = method;
            this.url = url;
        }

        public Builder header(String key, String value) {
            this.headers.put(key, value);
            return this;
        }

        public Builder body(String body) {
            this.body = body;
            return this;
        }

        public Builder timeout(int timeout) {
            this.timeout = timeout;
            return this;
        }

        public Builder followRedirects(boolean follow) {
            this.followRedirects = follow;
            return this;
        }

        public HttpRequest build() {
            return new HttpRequest(this);
        }
    }
}

// Usage — clean, readable, immutable
HttpRequest request = new HttpRequest.Builder("POST", "https://api.example.com/users")
    .header("Content-Type", "application/json")
    .header("Authorization", "Bearer token123")
    .body("{\"name\": \"John\"}")
    .timeout(5000)
    .build();
```

**Lombok @Builder Shortcut:**
```java
@Builder
@Getter
public class Employee {
    private String firstName;
    private String lastName;
    @Builder.Default
    private String department = "Engineering";
    private double salary;
}

// Usage
Employee emp = Employee.builder()
    .firstName("John")
    .lastName("Doe")
    .salary(150000)
    .build();
```

---

### 1.5 Prototype Pattern

**Intent:** Specify the kinds of objects to create using a prototypical instance, and create new objects by copying this prototype.

**When to Use:**
- When creating objects is expensive (database calls, network, complex computation)
- When you need to clone objects that have similar state
- When subclasses differ only in their initialization

**Implementation:**
```java
public class Document implements Cloneable {
    private String title;
    private String content;
    private List<String> tags;
    private Author author;

    // Shallow copy
    @Override
    public Document clone() {
        try {
            return (Document) super.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException("Clone failed", e);
        }
    }

    // Deep copy (required when containing mutable references)
    public Document deepClone() {
        try {
            Document cloned = (Document) super.clone();
            cloned.tags = new ArrayList<>(this.tags);            // Deep copy list
            cloned.author = new Author(this.author.getName());   // Deep copy object
            return cloned;
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException("Deep clone failed", e);
        }
    }
}

// Prototype Registry
public class DocumentRegistry {
    private Map<String, Document> prototypes = new HashMap<>();

    public void addPrototype(String key, Document prototype) {
        prototypes.put(key, prototype);
    }

    public Document getPrototype(String key) {
        return prototypes.get(key).deepClone();
    }
}
```

**Interview Q:** *What is the difference between shallow copy and deep copy in Prototype?*
**A:** Shallow copy duplicates the object's fields but not the objects referenced by those fields — both original and clone share the same referenced objects. Deep copy recursively copies all referenced objects, creating entirely independent duplicates. For immutable references (like Strings), shallow copy is safe; for mutable references (like Lists), deep copy is necessary to prevent unintended sharing.

---

## 2. Structural Patterns

Structural patterns deal with the composition of classes and objects to form larger structures while keeping them flexible and efficient.

---

### 2.1 Adapter Pattern

**Intent:** Convert the interface of a class into another interface that clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces.

**Diagram:**
```
┌──────────┐      ┌──────────────┐      ┌──────────────┐
│  Client   │─────►│   Adapter    │─────►│  Adaptee     │
├──────────┤      ├──────────────┤      ├──────────────┤
│          │      │ +request()   │      │+specificReq()│
└──────────┘      └──────────────┘      └──────────────┘
                         ▲
                  implements Target
```

**Implementation:**
```java
// Target interface (what the client expects)
public interface CustomerDataProvider {
    CustomerData getCustomerData(String customerId);
}

// Adaptee (third-party or legacy system)
public class LegacyCustomerSystem {
    public LegacyCustomerRecord fetchRecord(String id) {
        // Legacy format
        return new LegacyCustomerRecord(id, "John", "Doe", "555-1234");
    }
}

// Class Adapter (using inheritance)
public class CustomerDataAdapter extends LegacyCustomerSystem
        implements CustomerDataProvider {
    @Override
    public CustomerData getCustomerData(String customerId) {
        LegacyCustomerRecord record = fetchRecord(customerId);
        return new CustomerData(
            record.getId(),
            record.getFirstName() + " " + record.getLastName(),
            record.getPhone()
        );
    }
}

// Object Adapter (using composition — preferred)
public class CustomerDataAdapterComposition implements CustomerDataProvider {
    private final LegacyCustomerSystem legacySystem;

    public CustomerDataAdapterComposition(LegacyCustomerSystem legacySystem) {
        this.legacySystem = legacySystem;
    }

    @Override
    public CustomerData getCustomerData(String customerId) {
        LegacyCustomerRecord record = legacySystem.fetchRecord(customerId);
        return new CustomerData(
            record.getId(),
            record.getFirstName() + " " + record.getLastName(),
            record.getPhone()
        );
    }
}
```

**Real-World Java Example:** `java.util.Arrays.asList()` adapts an array to the `List` interface. `InputStreamReader` adapts `InputStream` to `Reader`.

---

### 2.2 Bridge Pattern

**Intent:** Decouple an abstraction from its implementation so that the two can vary independently.

**Diagram:**
```
┌──────────────┐         ┌──────────────────┐
│ Abstraction   │────────►│ Implementor      │
├──────────────┤         ├──────────────────┤
│ #impl        │         │ +operationImpl() │
│ +operation() │         └──────────────────┘
└──────┬───────┘                 ▲
       │                   ┌─────┴──────┐
  ┌────┴─────┐            │            │
  │Refined   │     ┌──────┴───┐  ┌─────┴────┐
  │Abstraction│    │Concrete  │  │Concrete  │
  └──────────┘    │ImplA     │  │ImplB     │
                  └──────────┘  └──────────┘
```

**Implementation:**
```java
// Implementor
public interface MessageSender {
    void sendMessage(String message);
}

// Concrete Implementors
public class EmailSender implements MessageSender {
    @Override
    public void sendMessage(String message) {
        System.out.println("Email: " + message);
    }
}

public class SlackSender implements MessageSender {
    @Override
    public void sendMessage(String message) {
        System.out.println("Slack: " + message);
    }
}

// Abstraction
public abstract class Notification {
    protected MessageSender sender;

    protected Notification(MessageSender sender) {
        this.sender = sender;
    }

    public abstract void notify(String message);
}

// Refined Abstraction
public class AlertNotification extends Notification {
    public AlertNotification(MessageSender sender) {
        super(sender);
    }

    @Override
    public void notify(String message) {
        sender.sendMessage("[ALERT] " + message);
    }
}

public class InfoNotification extends Notification {
    public InfoNotification(MessageSender sender) {
        super(sender);
    }

    @Override
    public void notify(String message) {
        sender.sendMessage("[INFO] " + message);
    }
}

// Usage — both dimensions vary independently
Notification alert = new AlertNotification(new SlackSender());
alert.notify("Server CPU usage > 90%");

Notification info = new InfoNotification(new EmailSender());
info.notify("Deployment completed successfully");
```

**Interview Q:** *When would you choose Bridge over Adapter?*
**A:** Bridge is designed upfront to separate abstraction from implementation, allowing both to evolve independently. Adapter is applied retroactively to make incompatible interfaces work together. Bridge is structural design; Adapter is structural repair.

---

### 2.3 Composite Pattern

**Intent:** Compose objects into tree structures to represent part-whole hierarchies. Composite lets clients treat individual objects and compositions uniformly.

**Diagram:**
```
         ┌──────────────┐
         │  Component   │
         ├──────────────┤
         │ +operation() │
         │ +add()       │
         │ +remove()    │
         └──────┬───────┘
                │
         ┌──────┴───────┐
         │              │
  ┌──────┴──────┐ ┌────┴───────┐
  │   Leaf      │ │ Composite  │
  ├─────────────┤ ├────────────┤
  │+operation() │ │-children   │
  └─────────────┘ │+operation()│
                  │+add()      │
                  │+remove()   │
                  └────────────┘
```

**Implementation:**
```java
// Component
public interface FileSystemComponent {
    long getSize();
    String getName();
    void print(String indent);
}

// Leaf
public class File implements FileSystemComponent {
    private String name;
    private long size;

    public File(String name, long size) {
        this.name = name;
        this.size = size;
    }

    @Override
    public long getSize() { return size; }

    @Override
    public String getName() { return name; }

    @Override
    public void print(String indent) {
        System.out.println(indent + "📄 " + name + " (" + size + " KB)");
    }
}

// Composite
public class Directory implements FileSystemComponent {
    private String name;
    private List<FileSystemComponent> children = new ArrayList<>();

    public Directory(String name) { this.name = name; }

    public void add(FileSystemComponent component) { children.add(component); }
    public void remove(FileSystemComponent component) { children.remove(component); }

    @Override
    public long getSize() {
        return children.stream().mapToLong(FileSystemComponent::getSize).sum();
    }

    @Override
    public String getName() { return name; }

    @Override
    public void print(String indent) {
        System.out.println(indent + "📁 " + name + "/");
        children.forEach(c -> c.print(indent + "  "));
    }
}

// Usage
Directory root = new Directory("root");
Directory src = new Directory("src");
src.add(new File("Main.java", 5));
src.add(new File("Utils.java", 3));
root.add(src);
root.add(new File("README.md", 2));
root.print("");  // Prints the tree
```

---

### 2.4 Decorator Pattern

**Intent:** Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality.

**Diagram:**
```
┌──────────────┐
│  Component   │◄──────────────────────┐
├──────────────┤                       │
│ +operation() │                       │
└──────┬───────┘                       │
       │                               │
┌──────┴──────┐   ┌────────────────────┴──┐
│ConcreteComp │   │      Decorator        │
├─────────────┤   ├───────────────────────┤
│+operation() │   │-component: Component  │
└─────────────┘   │+operation()           │
                  └───────────┬───────────┘
                              │
                    ┌─────────┴─────────┐
              ┌─────┴─────┐     ┌───────┴──────┐
              │Concrete   │     │Concrete      │
              │DecoratorA │     │DecoratorB    │
              └───────────┘     └──────────────┘
```

**Implementation:**
```java
// Component
public interface Coffee {
    String getDescription();
    double getCost();
}

// Concrete Component
public class SimpleCoffee implements Coffee {
    @Override
    public String getDescription() { return "Simple Coffee"; }
    @Override
    public double getCost() { return 5.00; }
}

// Base Decorator
public abstract class CoffeeDecorator implements Coffee {
    protected Coffee decoratedCoffee;

    public CoffeeDecorator(Coffee coffee) {
        this.decoratedCoffee = coffee;
    }
}

// Concrete Decorators
public class MilkDecorator extends CoffeeDecorator {
    public MilkDecorator(Coffee coffee) { super(coffee); }

    @Override
    public String getDescription() {
        return decoratedCoffee.getDescription() + ", Milk";
    }

    @Override
    public double getCost() {
        return decoratedCoffee.getCost() + 1.50;
    }
}

public class WhipDecorator extends CoffeeDecorator {
    public WhipDecorator(Coffee coffee) { super(coffee); }

    @Override
    public String getDescription() {
        return decoratedCoffee.getDescription() + ", Whip";
    }

    @Override
    public double getCost() {
        return decoratedCoffee.getCost() + 0.75;
    }
}

// Usage — dynamic composition
Coffee coffee = new SimpleCoffee();            // $5.00
coffee = new MilkDecorator(coffee);            // $6.50
coffee = new WhipDecorator(coffee);            // $7.25
System.out.println(coffee.getDescription() + " = $" + coffee.getCost());
// Output: Simple Coffee, Milk, Whip = $7.25
```

**Real-World Java Examples:**
- `java.io` — `BufferedInputStream` decorates `FileInputStream`
- `HttpServletRequestWrapper` in Servlet API
- Spring's `BeanPostProcessor` effectively decorates beans

---

### 2.5 Facade Pattern

**Intent:** Provide a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use.

**Implementation:**
```java
// Complex subsystem
public class InventorySystem {
    public boolean checkStock(String productId) { /* ... */ return true; }
    public void reserveItem(String productId) { /* ... */ }
}

public class PaymentSystem {
    public boolean charge(String accountId, double amount) { /* ... */ return true; }
    public void refund(String accountId, double amount) { /* ... */ }
}

public class ShippingSystem {
    public void scheduleDelivery(String address, String productId) { /* ... */ }
    public String getTrackingNumber() { return "TRK-12345"; }
}

// Facade
public class OrderFacade {
    private InventorySystem inventory;
    private PaymentSystem payment;
    private ShippingSystem shipping;

    public OrderFacade(InventorySystem inv, PaymentSystem pay, ShippingSystem ship) {
        this.inventory = inv;
        this.payment = pay;
        this.shipping = ship;
    }

    public String placeOrder(String productId, String accountId,
                              double amount, String address) {
        if (!inventory.checkStock(productId)) {
            throw new RuntimeException("Out of stock");
        }
        inventory.reserveItem(productId);

        if (!payment.charge(accountId, amount)) {
            throw new RuntimeException("Payment failed");
        }

        shipping.scheduleDelivery(address, productId);
        return shipping.getTrackingNumber();
    }
}

// Client — simple!
OrderFacade facade = new OrderFacade(inventory, payment, shipping);
String tracking = facade.placeOrder("PROD-1", "ACC-1", 29.99, "123 Main St");
```

---

### 2.6 Flyweight Pattern

**Intent:** Use sharing to support large numbers of fine-grained objects efficiently.

**When to Use:**
- When an application uses a large number of objects
- When storage costs are high due to the sheer quantity of objects
- When most object state can be made extrinsic (shared)

**Implementation:**
```java
// Flyweight (intrinsic state — shared)
public record TreeType(String name, String color, String texture) {}

// Flyweight Factory
public class TreeFactory {
    private static final Map<String, TreeType> treeTypes = new HashMap<>();

    public static TreeType getTreeType(String name, String color, String texture) {
        String key = name + "-" + color + "-" + texture;
        return treeTypes.computeIfAbsent(key, k -> new TreeType(name, color, texture));
    }

    public static int getTotalTypesCreated() { return treeTypes.size(); }
}

// Context (extrinsic state — unique per instance)
public class Tree {
    private int x, y;
    private TreeType type;  // Shared flyweight reference

    public Tree(int x, int y, TreeType type) {
        this.x = x;
        this.y = y;
        this.type = type;
    }

    public void draw() {
        System.out.println("Drawing " + type.name() + " at (" + x + "," + y + ")");
    }
}

// Usage — millions of trees, only a few TreeType objects
List<Tree> forest = new ArrayList<>();
TreeType oakType = TreeFactory.getTreeType("Oak", "Green", "Rough");
TreeType pineType = TreeFactory.getTreeType("Pine", "Dark Green", "Smooth");

for (int i = 0; i < 1_000_000; i++) {
    forest.add(new Tree(randomX(), randomY(), oakType));  // Shares same TreeType
    forest.add(new Tree(randomX(), randomY(), pineType)); // Shares same TreeType
}
// Only 2 TreeType objects created for 2M trees!
```

**Real-World Examples:**
- `String` pool in Java (interning)
- `Integer` cache for values -128 to 127
- `java.awt.Color` constants

---

### 2.7 Proxy Pattern

**Intent:** Provide a surrogate or placeholder for another object to control access to it.

**Types of Proxies:**
1. **Virtual Proxy** — Lazy initialization (create expensive object on demand)
2. **Protection Proxy** — Access control
3. **Remote Proxy** — Local representative for remote object (RMI)
4. **Smart Proxy** — Additional logic (caching, reference counting)

**Implementation — Virtual Proxy (Lazy Loading):**
```java
public interface Image {
    void display();
}

public class RealImage implements Image {
    private String filename;

    public RealImage(String filename) {
        this.filename = filename;
        loadFromDisk();  // Expensive operation
    }

    private void loadFromDisk() {
        System.out.println("Loading image: " + filename);
    }

    @Override
    public void display() {
        System.out.println("Displaying: " + filename);
    }
}

public class ProxyImage implements Image {
    private RealImage realImage;
    private String filename;

    public ProxyImage(String filename) {
        this.filename = filename;  // Does NOT load — deferred
    }

    @Override
    public void display() {
        if (realImage == null) {
            realImage = new RealImage(filename);  // Lazy load on first access
        }
        realImage.display();
    }
}
```

**Implementation — Protection Proxy:**
```java
public interface EmployeeDao {
    void create(String user, Employee emp);
    Employee read(String user, int id);
    void delete(String user, int id);
}

public class EmployeeDaoProxy implements EmployeeDao {
    private EmployeeDao realDao;
    private Map<String, Set<String>> permissions;

    public EmployeeDaoProxy(EmployeeDao realDao) {
        this.realDao = realDao;
        this.permissions = Map.of(
            "admin", Set.of("CREATE", "READ", "DELETE"),
            "manager", Set.of("CREATE", "READ"),
            "viewer", Set.of("READ")
        );
    }

    @Override
    public void create(String user, Employee emp) {
        if (hasPermission(user, "CREATE")) {
            realDao.create(user, emp);
        } else {
            throw new UnauthorizedException("No CREATE permission");
        }
    }
    // ... similar for read/delete
}
```

**Spring AOP Proxy Example:**
```java
// Spring creates JDK dynamic proxy or CGLIB proxy for @Transactional
@Service
@Transactional  // Spring wraps this bean in a proxy
public class OrderService {
    public void placeOrder(Order order) {
        // Proxy adds: start transaction
        // ... business logic
        // Proxy adds: commit/rollback transaction
    }
}
```

---

## 3. Behavioral Patterns

Behavioral patterns deal with algorithms and the assignment of responsibilities between objects.

---

### 3.1 Chain of Responsibility

**Intent:** Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request. Chain the receiving objects and pass the request along the chain.

**Diagram:**
```
Client ──► Handler1 ──► Handler2 ──► Handler3 ──► null
              │              │             │
           handles?       handles?      handles?
```

**Implementation:**
```java
public abstract class Handler {
    protected Handler next;

    public Handler setNext(Handler next) {
        this.next = next;
        return next;  // Enables fluent chaining
    }

    public abstract void handle(Request request);
}

public class AuthenticationHandler extends Handler {
    @Override
    public void handle(Request request) {
        if (!request.hasValidToken()) {
            throw new SecurityException("Invalid token");
        }
        System.out.println("Authentication passed");
        if (next != null) next.handle(request);
    }
}

public class AuthorizationHandler extends Handler {
    @Override
    public void handle(Request request) {
        if (!request.hasPermission()) {
            throw new SecurityException("Insufficient permissions");
        }
        System.out.println("Authorization passed");
        if (next != null) next.handle(request);
    }
}

public class LoggingHandler extends Handler {
    @Override
    public void handle(Request request) {
        System.out.println("Logging request: " + request.getId());
        if (next != null) next.handle(request);
    }
}

// Usage — build the chain
Handler chain = new LoggingHandler();
chain.setNext(new AuthenticationHandler())
     .setNext(new AuthorizationHandler());

chain.handle(request);  // Flows through: Log → AuthN → AuthZ
```

**Real-World Examples:**
- Servlet Filter Chain (`javax.servlet.Filter`)
- Spring Security Filter Chain
- `java.util.logging` Handler chain
- Apache Commons Chain

---

### 3.2 Command Pattern

**Intent:** Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.

**Implementation:**
```java
// Command interface
public interface Command {
    void execute();
    void undo();
}

// Receiver
public class Light {
    public void turnOn() { System.out.println("Light is ON"); }
    public void turnOff() { System.out.println("Light is OFF"); }
}

// Concrete Commands
public class LightOnCommand implements Command {
    private Light light;

    public LightOnCommand(Light light) { this.light = light; }

    @Override
    public void execute() { light.turnOn(); }
    @Override
    public void undo() { light.turnOff(); }
}

public class LightOffCommand implements Command {
    private Light light;

    public LightOffCommand(Light light) { this.light = light; }

    @Override
    public void execute() { light.turnOff(); }
    @Override
    public void undo() { light.turnOn(); }
}

// Invoker
public class RemoteControl {
    private Stack<Command> history = new Stack<>();
    private Command currentCommand;

    public void setCommand(Command command) { this.currentCommand = command; }

    public void pressButton() {
        currentCommand.execute();
        history.push(currentCommand);
    }

    public void pressUndo() {
        if (!history.isEmpty()) {
            history.pop().undo();
        }
    }
}
```

**Real-World Examples:**
- `Runnable` interface in Java
- Spring's `JdbcTemplate` with callback commands
- IDE undo/redo operations

---

### 3.3 Iterator Pattern

**Intent:** Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation.

**Implementation (Custom Iterator):**
```java
public class BinaryTree<T> implements Iterable<T> {
    private Node<T> root;

    // In-order iterator
    @Override
    public Iterator<T> iterator() {
        return new InOrderIterator(root);
    }

    private class InOrderIterator implements Iterator<T> {
        private Stack<Node<T>> stack = new Stack<>();

        InOrderIterator(Node<T> root) {
            pushLeft(root);
        }

        private void pushLeft(Node<T> node) {
            while (node != null) {
                stack.push(node);
                node = node.left;
            }
        }

        @Override
        public boolean hasNext() { return !stack.isEmpty(); }

        @Override
        public T next() {
            Node<T> node = stack.pop();
            pushLeft(node.right);
            return node.data;
        }
    }
}

// Usage — works with enhanced for-loop
for (String value : binaryTree) {
    System.out.println(value);
}
```

---

### 3.4 Mediator Pattern

**Intent:** Define an object that encapsulates how a set of objects interact. Mediator promotes loose coupling by keeping objects from referring to each other explicitly.

**Implementation:**
```java
// Mediator
public interface ChatMediator {
    void sendMessage(User user, String message);
    void addUser(User user);
}

// Concrete Mediator
public class ChatRoom implements ChatMediator {
    private List<User> users = new ArrayList<>();

    @Override
    public void addUser(User user) { users.add(user); }

    @Override
    public void sendMessage(User sender, String message) {
        for (User user : users) {
            if (user != sender) {  // Don't send to self
                user.receive(sender.getName() + ": " + message);
            }
        }
    }
}

// Colleague
public abstract class User {
    protected ChatMediator mediator;
    protected String name;

    public User(ChatMediator mediator, String name) {
        this.mediator = mediator;
        this.name = name;
    }

    public abstract void send(String message);
    public abstract void receive(String message);
    public String getName() { return name; }
}

public class ChatUser extends User {
    public ChatUser(ChatMediator mediator, String name) {
        super(mediator, name);
    }

    @Override
    public void send(String message) {
        System.out.println(name + " sends: " + message);
        mediator.sendMessage(this, message);
    }

    @Override
    public void receive(String message) {
        System.out.println(name + " receives: " + message);
    }
}
```

---

### 3.5 Memento Pattern

**Intent:** Without violating encapsulation, capture and externalize an object's internal state so that the object can be restored to this state later.

**Implementation:**
```java
// Memento
public class EditorMemento {
    private final String content;
    private final int cursorPosition;

    public EditorMemento(String content, int cursorPosition) {
        this.content = content;
        this.cursorPosition = cursorPosition;
    }

    public String getContent() { return content; }
    public int getCursorPosition() { return cursorPosition; }
}

// Originator
public class TextEditor {
    private String content = "";
    private int cursorPosition = 0;

    public void type(String text) {
        content += text;
        cursorPosition = content.length();
    }

    public EditorMemento save() {
        return new EditorMemento(content, cursorPosition);
    }

    public void restore(EditorMemento memento) {
        this.content = memento.getContent();
        this.cursorPosition = memento.getCursorPosition();
    }

    public String getContent() { return content; }
}

// Caretaker
public class EditorHistory {
    private Stack<EditorMemento> history = new Stack<>();

    public void push(EditorMemento memento) { history.push(memento); }
    public EditorMemento pop() { return history.pop(); }
}

// Usage
TextEditor editor = new TextEditor();
EditorHistory history = new EditorHistory();

editor.type("Hello ");
history.push(editor.save());

editor.type("World!");
history.push(editor.save());

editor.type(" Extra text");
editor.restore(history.pop());  // Back to "Hello World!"
```

---

### 3.6 Observer Pattern

**Intent:** Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.

**Diagram:**
```
┌──────────────┐         ┌──────────────┐
│  Subject     │────────►│  Observer    │
├──────────────┤         ├──────────────┤
│-observers   │         │+update()     │
│+attach()    │         └──────────────┘
│+detach()    │                ▲
│+notify()    │         ┌──────┴──────┐
└──────────────┘         │             │
                   ┌─────┴───┐  ┌─────┴────┐
                   │Concrete │  │Concrete  │
                   │Observer1│  │Observer2 │
                   └─────────┘  └──────────┘
```

**Implementation:**
```java
// Observer interface
public interface StockObserver {
    void onPriceChange(String symbol, double price);
}

// Subject
public class StockMarket {
    private List<StockObserver> observers = new CopyOnWriteArrayList<>();
    private Map<String, Double> prices = new ConcurrentHashMap<>();

    public void addObserver(StockObserver observer) { observers.add(observer); }
    public void removeObserver(StockObserver observer) { observers.remove(observer); }

    public void setPrice(String symbol, double price) {
        double oldPrice = prices.getOrDefault(symbol, 0.0);
        prices.put(symbol, price);
        if (oldPrice != price) {
            notifyObservers(symbol, price);
        }
    }

    private void notifyObservers(String symbol, double price) {
        observers.forEach(obs -> obs.onPriceChange(symbol, price));
    }
}

// Concrete Observers
public class PortfolioDisplay implements StockObserver {
    @Override
    public void onPriceChange(String symbol, double price) {
        System.out.println("Portfolio: " + symbol + " is now $" + price);
    }
}

public class AlertSystem implements StockObserver {
    @Override
    public void onPriceChange(String symbol, double price) {
        if (price > 1000) {
            System.out.println("ALERT: " + symbol + " exceeded $1000!");
        }
    }
}
```

**Java Built-in Support:**
```java
// java.util.Observable (deprecated in Java 9) — use java.beans.PropertyChangeListener
// Or use reactive streams: Flow.Subscriber / Flow.Publisher (Java 9+)
// Or Project Reactor / RxJava

// Spring Event System
@Component
public class OrderCreatedListener {
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        System.out.println("Order created: " + event.getOrderId());
    }
}

@Component
public class OrderService {
    @Autowired
    private ApplicationEventPublisher publisher;

    public void createOrder(Order order) {
        // ... save order
        publisher.publishEvent(new OrderCreatedEvent(order.getId()));
    }
}
```

---

### 3.7 State Pattern

**Intent:** Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.

**Implementation:**
```java
// State interface
public interface OrderState {
    void next(OrderContext context);
    void prev(OrderContext context);
    String getStatus();
}

// Concrete States
public class CreatedState implements OrderState {
    @Override
    public void next(OrderContext context) {
        context.setState(new ConfirmedState());
    }
    @Override
    public void prev(OrderContext context) {
        System.out.println("Already at initial state");
    }
    @Override
    public String getStatus() { return "CREATED"; }
}

public class ConfirmedState implements OrderState {
    @Override
    public void next(OrderContext context) {
        context.setState(new ShippedState());
    }
    @Override
    public void prev(OrderContext context) {
        context.setState(new CreatedState());
    }
    @Override
    public String getStatus() { return "CONFIRMED"; }
}

public class ShippedState implements OrderState {
    @Override
    public void next(OrderContext context) {
        context.setState(new DeliveredState());
    }
    @Override
    public void prev(OrderContext context) {
        context.setState(new ConfirmedState());
    }
    @Override
    public String getStatus() { return "SHIPPED"; }
}

public class DeliveredState implements OrderState {
    @Override
    public void next(OrderContext context) {
        System.out.println("Order is already delivered");
    }
    @Override
    public void prev(OrderContext context) {
        context.setState(new ShippedState());
    }
    @Override
    public String getStatus() { return "DELIVERED"; }
}

// Context
public class OrderContext {
    private OrderState state;

    public OrderContext() { this.state = new CreatedState(); }
    public void setState(OrderState state) { this.state = state; }

    public void nextState() { state.next(this); }
    public void prevState() { state.prev(this); }
    public String getStatus() { return state.getStatus(); }
}
```

---

### 3.8 Strategy Pattern

**Intent:** Define a family of algorithms, encapsulate each one, and make them interchangeable. Strategy lets the algorithm vary independently from clients that use it.

**Implementation:**
```java
// Strategy interface
public interface PaymentStrategy {
    boolean pay(double amount);
}

// Concrete Strategies
public class CreditCardPayment implements PaymentStrategy {
    private String cardNumber;
    public CreditCardPayment(String cardNumber) { this.cardNumber = cardNumber; }

    @Override
    public boolean pay(double amount) {
        System.out.println("Paying $" + amount + " with Credit Card: " + cardNumber);
        return true;
    }
}

public class UPIPayment implements PaymentStrategy {
    private String upiId;
    public UPIPayment(String upiId) { this.upiId = upiId; }

    @Override
    public boolean pay(double amount) {
        System.out.println("Paying $" + amount + " via UPI: " + upiId);
        return true;
    }
}

public class CryptoPayment implements PaymentStrategy {
    private String walletAddress;

    public CryptoPayment(String walletAddress) { this.walletAddress = walletAddress; }

    @Override
    public boolean pay(double amount) {
        System.out.println("Paying $" + amount + " via Crypto: " + walletAddress);
        return true;
    }
}

// Context
public class ShoppingCart {
    private PaymentStrategy paymentStrategy;

    public void setPaymentStrategy(PaymentStrategy strategy) {
        this.paymentStrategy = strategy;
    }

    public void checkout(double amount) {
        paymentStrategy.pay(amount);
    }
}

// Usage — switch strategy at runtime
ShoppingCart cart = new ShoppingCart();
cart.setPaymentStrategy(new CreditCardPayment("4111-1111-1111-1111"));
cart.checkout(100.0);

cart.setPaymentStrategy(new UPIPayment("user@upi"));
cart.checkout(50.0);
```

**Spring Integration:**
```java
@Service
public class PricingService {
    private final Map<String, PricingStrategy> strategies;

    public PricingService(List<PricingStrategy> strategyList) {
        this.strategies = strategyList.stream()
            .collect(Collectors.toMap(
                s -> s.getClass().getSimpleName(),
                Function.identity()
            ));
    }

    public double calculatePrice(String strategyName, Order order) {
        PricingStrategy strategy = strategies.get(strategyName);
        if (strategy == null) throw new IllegalArgumentException("Unknown strategy");
        return strategy.calculate(order);
    }
}
```

---

### 3.9 Template Method Pattern

**Intent:** Define the skeleton of an algorithm in an operation, deferring some steps to subclasses. Template Method lets subclasses redefine certain steps of an algorithm without changing its structure.

**Implementation:**
```java
public abstract class DataParser {
    // Template method — defines the algorithm skeleton
    public final void parse(String filePath) {
        String rawData = readFile(filePath);
        Data parsedData = processData(rawData);
        saveData(parsedData);
        sendNotification();
    }

    // Common implementation
    private String readFile(String filePath) {
        System.out.println("Reading file: " + filePath);
        return "raw data from " + filePath;
    }

    // Abstract — subclasses must implement
    protected abstract Data processData(String rawData);

    // Hook method — optional override
    protected void saveData(Data data) {
        System.out.println("Saving to default database");
    }

    // Hook method — subclasses can override
    protected void sendNotification() {
        // Default: no notification
    }
}

public class CSVParser extends DataParser {
    @Override
    protected Data processData(String rawData) {
        System.out.println("Parsing CSV data");
        return new Data(rawData.split(","));
    }

    @Override
    protected void sendNotification() {
        System.out.println("CSV parsing complete — notification sent");
    }
}

public class JSONParser extends DataParser {
    @Override
    protected Data processData(String rawData) {
        System.out.println("Parsing JSON data");
        return new Data(rawData);  // Simplified
    }

    @Override
    protected void saveData(Data data) {
        System.out.println("Saving to NoSQL database");
    }
}
```

**Real-World Examples:**
- `AbstractList` — `addAll()` calls `add()` (template method)
- Spring's `AbstractApplicationContext.refresh()` — template method for context initialization
- `HttpServlet.doGet()/doPost()` called by `service()` template method

---

### 3.10 Visitor Pattern

**Intent:** Represent an operation to be performed on elements of an object structure. Visitor lets you define new operations without changing the classes of the elements.

**Implementation:**
```java
// Visitor interface
public interface DocumentVisitor {
    void visit(Paragraph paragraph);
    void visit(Image image);
    void visit(Table table);
}

// Element interface
public interface DocumentElement {
    void accept(DocumentVisitor visitor);
}

// Concrete Elements
public class Paragraph implements DocumentElement {
    private String text;

    public Paragraph(String text) { this.text = text; }
    public String getText() { return text; }

    @Override
    public void accept(DocumentVisitor visitor) {
        visitor.visit(this);  // Double dispatch
    }
}

public class Image implements DocumentElement {
    private String url;

    public Image(String url) { this.url = url; }
    public String getUrl() { return url; }

    @Override
    public void accept(DocumentVisitor visitor) {
        visitor.visit(this);
    }
}

public class Table implements DocumentElement {
    private String[][] data;

    public Table(String[][] data) { this.data = data; }
    public String[][] getData() { return data; }

    @Override
    public void accept(DocumentVisitor visitor) {
        visitor.visit(this);
    }
}

// Concrete Visitors
public class HTMLExportVisitor implements DocumentVisitor {
    @Override
    public void visit(Paragraph p) {
        System.out.println("<p>" + p.getText() + "</p>");
    }

    @Override
    public void visit(Image img) {
        System.out.println("<img src=\"" + img.getUrl() + "\" />");
    }

    @Override
    public void visit(Table table) {
        System.out.println("<table>...</table>");
    }
}

public class MarkdownExportVisitor implements DocumentVisitor {
    @Override
    public void visit(Paragraph p) {
        System.out.println(p.getText() + "\n");
    }

    @Override
    public void visit(Image img) {
        System.out.println("!(" + img.getUrl() + ")");
    }

    @Override
    public void visit(Table table) {
        System.out.println("| ... |");  // Markdown table
    }
}

// Usage
List<DocumentElement> document = List.of(
    new Paragraph("Hello World"),
    new Image("photo.png"),
    new Table(new String[][]{{"A", "B"}})
);

DocumentVisitor htmlExporter = new HTMLExportVisitor();
document.forEach(el -> el.accept(htmlExporter));
```

---

## 4. Concurrency Patterns

### 4.1 Producer-Consumer Pattern

**Implementation with BlockingQueue:**
```java
public class ProducerConsumerDemo {
    private final BlockingQueue<Task> queue = new LinkedBlockingQueue<>(100);

    class Producer implements Runnable {
        @Override
        public void run() {
            try {
                while (true) {
                    Task task = generateTask();
                    queue.put(task);  // Blocks if queue is full
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    class Consumer implements Runnable {
        @Override
        public void run() {
            try {
                while (true) {
                    Task task = queue.take();  // Blocks if queue is empty
                    processTask(task);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
}
```

### 4.2 Read-Write Lock Pattern

```java
public class ThreadSafeCache<K, V> {
    private final Map<K, V> cache = new HashMap<>();
    private final ReadWriteLock lock = new ReentrantReadWriteLock();

    public V get(K key) {
        lock.readLock().lock();
        try {
            return cache.get(key);
        } finally {
            lock.readLock().unlock();
        }
    }

    public void put(K key, V value) {
        lock.writeLock().lock();
        try {
            cache.put(key, value);
        } finally {
            lock.writeLock().unlock();
        }
    }
}
```

### 4.3 Thread Pool Pattern

```java
// Custom thread pool with monitoring
ExecutorService executor = new ThreadPoolExecutor(
    10,                                    // Core pool size
    50,                                    // Max pool size
    60L, TimeUnit.SECONDS,                 // Keep-alive time
    new LinkedBlockingQueue<>(1000),       // Work queue
    new ThreadFactoryBuilder()             // Custom thread factory
        .setNameFormat("worker-%d")
        .setDaemon(true)
        .build(),
    new ThreadPoolExecutor.CallerRunsPolicy()  // Rejection handler
);

// Monitor active threads and queue size
ThreadPoolExecutor tpe = (ThreadPoolExecutor) executor;
System.out.println("Active: " + tpe.getActiveCount());
System.out.println("Queue size: " + tpe.getQueue().size());
```

### 4.4 Fork-Join Pattern

```java
public class ParallelSumTask extends RecursiveTask<Long> {
    private static final int THRESHOLD = 10_000;
    private final long[] array;
    private final int start, end;

    public ParallelSumTask(long[] array, int start, int end) {
        this.array = array;
        this.start = start;
        this.end = end;
    }

    @Override
    protected Long compute() {
        if (end - start <= THRESHOLD) {
            long sum = 0;
            for (int i = start; i < end; i++) sum += array[i];
            return sum;
        }
        int mid = (start + end) / 2;
        ParallelSumTask left = new ParallelSumTask(array, start, mid);
        ParallelSumTask right = new ParallelSumTask(array, mid, end);
        left.fork();                    // Async execute left
        long rightResult = right.compute(); // Execute right in current thread
        long leftResult = left.join();  // Wait for left
        return leftResult + rightResult;
    }
}

// Usage
ForkJoinPool pool = ForkJoinPool.commonPool();
long result = pool.invoke(new ParallelSumTask(array, 0, array.length));
```

### 4.5 CompletableFuture Composition

```java
public class OrderService {
    public CompletableFuture<OrderResult> processOrder(Order order) {
        return validateOrder(order)
            .thenCompose(this::checkInventory)
            .thenCompose(this::processPayment)
            .thenCompose(this::scheduleShipping)
            .thenApply(this::buildResult)
            .exceptionally(ex -> {
                log.error("Order processing failed", ex);
                return OrderResult.failed(ex.getMessage());
            });
    }

    private CompletableFuture<Order> validateOrder(Order order) {
        return CompletableFuture.supplyAsync(() -> {
            if (order.getItems().isEmpty()) throw new IllegalArgumentException("Empty order");
            return order;
        }, validationExecutor);
    }

    // Parallel composition
    public CompletableFuture<EnrichedOrder> enrichOrder(Order order) {
        CompletableFuture<Customer> customerFuture =
            CompletableFuture.supplyAsync(() -> customerService.getCustomer(order.getCustomerId()));
        CompletableFuture<List<Inventory>> inventoryFuture =
            CompletableFuture.supplyAsync(() -> inventoryService.checkStock(order.getItems()));
        CompletableFuture<Pricing> pricingFuture =
            CompletableFuture.supplyAsync(() -> pricingService.calculate(order));

        return CompletableFuture.allOf(customerFuture, inventoryFuture, pricingFuture)
            .thenApply(v -> new EnrichedOrder(
                customerFuture.join(),
                inventoryFuture.join(),
                pricingFuture.join()
            ));
    }
}
```

---

## 5. Architectural Patterns

### 5.1 MVC (Model-View-Controller)

```
┌─────────┐     ┌──────────────┐     ┌───────────┐
│  Model   │◄────│  Controller  │────►│   View    │
│(Business │     │ (Orchestrator│     │(Presentation
│  Logic)  │────►│  /Input)     │◄────│  /Output) │
└─────────┘     └──────────────┘     └───────────┘
     ▲                                       │
     └───────────────────────────────────────┘
           View pulls from Model
```

- **Spring MVC** — Controller (`@Controller`), View (Thymeleaf/JSP), Model (`@ModelAttribute`)

### 5.2 Layered Architecture

```
┌─────────────────────────────┐
│     Presentation Layer      │  ← REST Controllers, DTOs
├─────────────────────────────┤
│     Application Layer       │  ← Service classes, Use Cases
├─────────────────────────────┤
│     Domain Layer            │  ← Entities, Business Rules
├─────────────────────────────┤
│     Infrastructure Layer    │  ← Repositories, External APIs
└─────────────────────────────┘
```

### 5.3 Hexagonal Architecture (Ports & Adapters)

```
         ┌──────────────────┐
         │   Domain Core    │
         │  (Business Rules)│
         └────────┬─────────┘
                  │
         ┌────────┴─────────┐
         │      Ports       │
         │  (Interfaces)    │
         └────────┬─────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
┌────┴────┐  ┌───┴────┐  ┌───┴─────┐
│REST     │  │Database│  │Message  │
│Adapter  │  │Adapter │  │Adapter  │
└─────────┘  └────────┘  └─────────┘
```

### 5.4 CQRS (Command Query Responsibility Segregation)

```
┌──────────────┐         ┌──────────────┐
│  Command Side│         │   Query Side │
├──────────────┤         ├──────────────┤
│ Commands     │         │  Queries     │
│ Aggregates   │         │  Read Models │
│ Write DB     │         │  Read DB     │
└──────┬───────┘         └──────▲───────┘
       │                        │
       │    ┌───────────┐      │
       └───►│  Event Bus├──────┘
            └───────────┘
        (Sync events to read model)
```

### 5.5 Event Sourcing

```java
// Instead of storing current state, store all events
public class EventSourcedAccount {
    private List<AccountEvent> events = new ArrayList<>();

    public void apply(DepositEvent event) {
        events.add(event);
    }

    public void apply(WithdrawalEvent event) {
        events.add(event);
    }

    // Reconstruct state by replaying events
    public double getBalance() {
        return events.stream()
            .mapToDouble(e -> {
                if (e instanceof DepositEvent) return e.getAmount();
                if (e instanceof WithdrawalEvent) return -e.getAmount();
                return 0;
            })
            .sum();
    }
}
```

---

# Part II: Microservices Design Patterns

## 1. API Gateway Pattern

**Problem:** Clients need to interact with multiple microservices, each with its own endpoint, authentication, and protocol.

**Solution:** A single entry point that routes requests to appropriate services, handles cross-cutting concerns, and aggregates responses.

```
┌───────┐     ┌──────────────┐     ┌──────────┐
│Mobile │────►│              │────►│User Svc  │
└───────┘     │              │     └──────────┘
┌───────┐     │  API Gateway │     ┌──────────┐
│ Web   │────►│              │────►│Order Svc │
└───────┘     │  - Routing   │     └──────────┘
┌───────┐     │  - Auth      │     ┌──────────┐
│Partner│────►│  - Rate Limit│────►│Product   │
└───────┘     │  - Caching   │     │  Svc     │
              └──────────────┘     └──────────┘
```

**Implementation (Spring Cloud Gateway):**
```java
@Configuration
public class GatewayConfig {
    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("user-service", r -> r
                .path("/api/users/**")
                .filters(f -> f
                    .addRequestHeader("X-Gateway", "api-gateway")
                    .circuitBreaker(config -> config
                        .setName("userCircuitBreaker")
                        .setFallbackUri("forward:/fallback/users"))
                    .retry(config -> config
                        .setRetries(3)
                        .setStatuses(HttpStatus.GATEWAY_TIMEOUT)))
                .uri("lb://user-service"))
            .route("order-service", r -> r
                .path("/api/orders/**")
                .filters(f -> f
                    .requestRateLimiter(config -> config
                        .setRateLimiter(redisRateLimiter())))
                .uri("lb://order-service"))
            .build();
    }
}
```

---

## 2. Saga Pattern (Distributed Transactions)

**Problem:** How to maintain data consistency across microservices without traditional ACID transactions.

**Solution:** A saga is a sequence of local transactions where each step publishes an event that triggers the next step. If a step fails, saga executes compensating transactions to undo preceding steps.

### 2.1 Choreography-Based Saga

```
Order Service          Payment Service         Inventory Service
     │                       │                        │
     │──createOrder──────►   │                        │
     │   OrderCreated        │                        │
     │                       │──processPayment──►     │
     │                       │   PaymentProcessed     │
     │                       │                        │──reserveItems──►
     │                       │                        │   InventoryReserved
     │◄──OrderCompleted──────│                        │
```

```java
// Choreography — each service emits and listens to events
@Service
public class OrderService {
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;

    @Transactional
    public Order createOrder(OrderRequest request) {
        Order order = new Order(request);
        order.setStatus(Status.PENDING);
        orderRepository.save(order);

        // Emit event — other services react
        kafkaTemplate.send("order-events",
            new OrderCreatedEvent(order.getId(), order.getCustomerId(), order.getTotal()));

        return order;
    }

    @KafkaListener(topics = "payment-events")
    public void handlePaymentEvent(PaymentEvent event) {
        if (event.getStatus() == PaymentStatus.COMPLETED) {
            orderRepository.findById(event.getOrderId())
                .ifPresent(order -> {
                    order.setStatus(Status.CONFIRMED);
                    orderRepository.save(order);
                });
        } else if (event.getStatus() == PaymentStatus.FAILED) {
            // Compensating transaction
            orderRepository.findById(event.getOrderId())
                .ifPresent(order -> {
                    order.setStatus(Status.CANCELLED);
                    orderRepository.save(order);
                });
        }
    }
}
```

### 2.2 Orchestration-Based Saga

```java
// Orchestrator — centralized controller
@Service
public class OrderSagaOrchestrator {
    @Autowired
    private KafkaTemplate<String, SagaCommand> kafkaTemplate;

    public void executeSaga(Order order) {
        // Step 1: Create Order
        Order created = orderService.create(order);
        sagaState.put(created.getId(), SagaStep.ORDER_CREATED);

        // Step 2: Process Payment
        kafkaTemplate.send("saga-commands",
            new ProcessPaymentCommand(created.getId(), created.getTotal()));

        // Next steps triggered by event responses
    }

    @KafkaListener(topics = "saga-responses")
    public void handleSagaResponse(SagaResponse response) {
        SagaStep currentStep = sagaState.get(response.getOrderId());

        switch (currentStep) {
            case ORDER_CREATED:
                if (response.isSuccess()) {
                    kafkaTemplate.send("saga-commands",
                        new ReserveInventoryCommand(response.getOrderId()));
                    sagaState.put(response.getOrderId(), SagaStep.PAYMENT_PROCESSED);
                } else {
                    compensateOrderCreated(response.getOrderId());
                }
                break;
            case PAYMENT_PROCESSED:
                if (response.isSuccess()) {
                    sagaState.put(response.getOrderId(), SagaStep.COMPLETED);
                } else {
                    compensatePaymentProcessed(response.getOrderId());
                }
                break;
        }
    }

    private void compensatePaymentProcessed(String orderId) {
        kafkaTemplate.send("saga-commands", new RefundPaymentCommand(orderId));
        kafkaTemplate.send("saga-commands", new CancelOrderCommand(orderId));
    }
}
```

**Interview Q:** *Choreography vs Orchestration — when to use which?*
**A:** Choreography is better for simple sagas (2-4 steps) with few services — it's loosely coupled but harder to debug and monitor. Orchestration is better for complex sagas with many steps — it provides central control, easier monitoring, and clearer error handling, but adds a single point of coordination.

---

## 3. Circuit Breaker Pattern

**Problem:** When a downstream service is failing, repeated calls waste resources and can cause cascading failures.

**Solution:** Wrap calls in a circuit breaker that monitors failures and "trips" (opens) when failures exceed a threshold, preventing further calls for a cooldown period.

```
         CLOSED (Normal)
          │
          │ failures >= threshold
          ▼
        OPEN (Blocking)
          │
          │ after timeout
          ▼
      HALF-OPEN (Testing)
       │           │
   success     failure
       │           │
       ▼           ▼
    CLOSED       OPEN
```

**Implementation (Resilience4j):**
```java
@Configuration
public class CircuitBreakerConfig {

    @Bean
    public CircuitBreaker orderServiceCircuitBreaker() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)                    // Trip at 50% failure rate
            .waitDurationInOpenState(Duration.ofSeconds(30))  // Wait 30s before half-open
            .slidingWindowSize(10)                       // Consider last 10 calls
            .slidingWindowType(SlidingWindowType.COUNT_BASED)
            .permittedNumberOfCallsInHalfOpenState(3)    // Allow 3 test calls
            .slowCallDurationThreshold(Duration.ofSeconds(5))  // 5s = slow call
            .slowCallRateThreshold(80)                   // Trip at 80% slow calls
            .build();

        return CircuitBreaker.of("orderService", config);
    }
}

@Service
public class OrderClient {
    private final CircuitBreaker circuitBreaker;

    @CircuitBreaker(name = "orderService", fallbackMethod = "getOrderFallback")
    @Retry(name = "orderService", fallbackMethod = "getOrderFallback")
    @TimeLimiter(name = "orderService")
    public CompletableFuture<Order> getOrder(String orderId) {
        return CompletableFuture.supplyAsync(() ->
            restTemplate.getForObject("/orders/" + orderId, Order.class));
    }

    public CompletableFuture<Order> getOrderFallback(String orderId, Exception ex) {
        // Fallback: return cached/default response
        return CompletableFuture.completedFuture(
            Order.builder()
                .id(orderId)
                .status(Status.UNKNOWN)
                .message("Service temporarily unavailable")
                .build()
        );
    }
}
```

---

## 4. CQRS (Command Query Responsibility Segregation)

**Problem:** Read and write workloads often have vastly different scaling, performance, and data model requirements.

**Solution:** Separate the read model from the write model. Commands mutate state; queries read state. Each can be optimized independently.

```
┌──────────────────────────────────────────────────────┐
│                    CQRS Architecture                  │
│                                                      │
│  ┌─────────────┐    Events    ┌───────────────┐     │
│  │ Command Side │────────────►│  Event Store   │     │
│  │              │             │               │     │
│  │ - Validators │             └───────┬───────┘     │
│  │ - Aggregates │                     │             │
│  │ - Write DB   │              Event Handler        │
│  └──────┬───────┘                     │             │
│         │                    ┌────────▼────────┐    │
│    Command Handler           │   Query Side     │    │
│                              │                  │    │
│                              │ - Read Models    │    │
│                              │ - Projections    │    │
│                              │ - Read DB        │    │
│                              └──────────────────┘    │
└──────────────────────────────────────────────────────┘
```

**Implementation (Axon Framework):**
```java
// Command
public class CreateOrderCommand {
    @TargetAggregateIdentifier
    private final String orderId;
    private final String customerId;
    private final List<OrderLine> items;
}

// Aggregate (Write Model)
@Aggregate
public class OrderAggregate {
    @AggregateIdentifier
    private String orderId;
    private OrderStatus status;

    @CommandHandler
    public OrderAggregate(CreateOrderCommand cmd) {
        apply(new OrderCreatedEvent(cmd.getOrderId(), cmd.getCustomerId(), cmd.getItems()));
    }

    @EventSourcingHandler
    public void on(OrderCreatedEvent event) {
        this.orderId = event.getOrderId();
        this.status = OrderStatus.CREATED;
    }
}

// Query
public class FindOrderQuery {
    private final String orderId;
}

// Projection (Read Model)
@Component
public class OrderProjection {
    @Autowired
    private OrderReadRepository repository;

    @QueryHandler
    public OrderSummary handle(FindOrderQuery query) {
        return repository.findById(query.getOrderId())
            .map(this::toSummary)
            .orElseThrow(() -> new OrderNotFoundException(query.getOrderId()));
    }

    @EventHandler
    public void on(OrderCreatedEvent event) {
        // Update read model
        OrderReadModel model = new OrderReadModel();
        model.setOrderId(event.getOrderId());
        model.setCustomerId(event.getCustomerId());
        model.setStatus(OrderStatus.CREATED.name());
        repository.save(model);
    }
}
```

---

## 5. Event Sourcing Pattern

**Problem:** Traditional CRUD only stores current state, losing the history of how the state evolved.

**Solution:** Store all state-changing events as the source of truth. Current state is derived by replaying events.

```java
// Event Store
public class EventStore {
    private final JdbcTemplate jdbcTemplate;

    public void append(String aggregateId, DomainEvent event) {
        String payload = serialize(event);
        jdbcTemplate.update(
            "INSERT INTO events (aggregate_id, event_type, payload, version, timestamp) " +
            "VALUES (?, ?, ?, ?, ?)",
            aggregateId, event.getClass().getSimpleName(), payload,
            event.getVersion(), Instant.now()
        );
    }

    public List<DomainEvent> loadEvents(String aggregateId) {
        return jdbcTemplate.query(
            "SELECT * FROM events WHERE aggregate_id = ? ORDER BY version",
            (rs, rowNum) -> deserialize(rs.getString("payload"), rs.getString("event_type")),
            aggregateId
        );
    }
}

// Aggregate with Event Sourcing
public class BankAccount {
    private String accountId;
    private double balance;
    private List<DomainEvent> uncommittedEvents = new ArrayList<>();

    // Factory method — create from events
    public static BankAccount fromEvents(List<DomainEvent> events) {
        BankAccount account = new BankAccount();
        events.forEach(account::apply);
        return account;
    }

    // Business methods — produce events
    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("Amount must be positive");
        apply(new MoneyDepositedEvent(accountId, amount, balance + amount));
    }

    public void withdraw(double amount) {
        if (amount > balance) throw new InsufficientFundsException();
        apply(new MoneyWithdrawnEvent(accountId, amount, balance - amount));
    }

    // Apply event — update state
    private void apply(DomainEvent event) {
        if (event instanceof AccountCreatedEvent e) {
            this.accountId = e.getAccountId();
            this.balance = 0;
        } else if (event instanceof MoneyDepositedEvent e) {
            this.balance = e.getNewBalance();
        } else if (event instanceof MoneyWithdrawnEvent e) {
            this.balance = e.getNewBalance();
        }
        uncommittedEvents.add(event);
    }

    public List<DomainEvent> getUncommittedEvents() {
        return Collections.unmodifiableList(uncommittedEvents);
    }
}
```

---

## 6. Strangler Fig Pattern

**Problem:** How to migrate from a monolith to microservices without a big-bang rewrite.

**Solution:** Incrementally replace parts of the monolith by building new services alongside it, routing traffic gradually.

```
Phase 1:                    Phase 2:                    Phase 3:
┌──────────┐               ┌──────────┐               ┌──────────┐
│Monolith  │               │Monolith  │               │Monolith  │
│(all func)│               │(partial) │               │(minimal) │
└────┬─────┘               └────┬─────┘               └──────────┘
     │                          │                        │
     ▼                          ▼                        ▼
  Gateway                   Gateway                   Gateway
     │                          │                     ┌──┴──┐
     │                     ┌────┴────┐                │     │
     │                     │         │            ┌───┘     └───┐
     │                  New Svc   New Svc       ┌──┴──┐   ┌──┴──┐
     │                     │         │         │Svc A │...│Svc Z│
     ▼                     ▼         ▼         └─────┘   └─────┘
  Client                 Client                 Client
```

---

## 7. Sidecar Pattern

**Problem:** Cross-cutting concerns (logging, monitoring, security) need to be implemented consistently across services in different languages.

**Solution:** Deploy a helper container (sidecar) alongside each service that handles these concerns.

```
┌──────────────────────────────────┐
│             Pod                  │
│  ┌──────────┐   ┌────────────┐  │
│  │Application│◄─►│  Sidecar   │  │
│  │Container  │   │ (Envoy/   │  │
│  │           │   │  Istio)   │  │
│  └──────────┘   └────────────┘  │
└──────────────────────────────────┘
```

---

## 8. BFF (Backend for Frontend) Pattern

**Problem:** Different client types (mobile, web, IoT) need different API shapes and data granularity.

**Solution:** Create a dedicated backend service for each frontend type.

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Mobile  │     │   Web    │     │   IoT    │
│   App    │     │  Client  │     │  Device  │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     ▼                ▼                ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Mobile   │    │   Web    │    │   IoT    │
│   BFF    │    │   BFF    │    │   BFF    │
└────┬─────┘    └────┬─────┘    └────┬─────┘
     │                │                │
     └────────────────┼────────────────┘
                      │
              ┌───────┴───────┐
              │  Microservices│
              └───────────────┘
```

---

## 9. Bulkhead Pattern

**Problem:** A failure in one service can consume all resources and cascade to other services.

**Solution:** Isolate different services or operations into separate resource pools (thread pools, connection pools) so that a failure in one doesn't affect others.

```java
// Resilience4j Bulkhead
@Service
public class ExternalServiceClient {

    @Bulkhead(name = "serviceA", type = Bulkhead.Type.SEMAPHORE)
    public String callServiceA() {
        return restTemplate.getForObject("/service-a/data", String.class);
    }

    @Bulkhead(name = "serviceB", type = Bulkhead.Type.THREADPOOL)
    @TimeLimiter(name = "serviceB")
    public CompletableFuture<String> callServiceB() {
        return CompletableFuture.supplyAsync(() ->
            restTemplate.getForObject("/service-b/data", String.class));
    }
}

// Configuration
@Bean
public Customizer<BulkheadRegistry> bulkheadCustomizer() {
    return registry -> {
        BulkheadConfig serviceAConfig = BulkheadConfig.custom()
            .maxConcurrentCalls(10)     // Max 10 concurrent calls
            .maxWaitDuration(Duration.ofMillis(500))
            .build();

        ThreadPoolBulkheadConfig serviceBConfig = ThreadPoolBulkheadConfig.custom()
            .maxThreadPoolSize(20)
            .coreThreadPoolSize(10)
            .queueCapacity(50)
            .build();

        registry.addConfiguration("serviceA", serviceAConfig);
    };
}
```

---

## 10. Service Discovery Pattern

**Problem:** In a dynamic microservices environment, service instances come and go. How do clients find available instances?

**Solution:** Use a service registry that services register with and clients discover from.

```
┌──────────┐  register   ┌──────────────┐  register  ┌──────────┐
│Service A │─────────────►│              │◄───────────│Service B │
└──────────┘             │   Service    │            └──────────┘
                         │   Registry   │
┌──────────┐  discover   │  (Eureka/    │
│  Client  │─────────────►│   Consul)   │
└──────────┘             └──────────────┘
```

**Implementation (Spring Cloud Netflix Eureka):**
```java
// Eureka Server
@SpringBootApplication
@EnableEurekaServer
public class EurekaServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(EurekaServerApplication.class, args);
    }
}

// Service Registration (application.yml)
// eureka.client.service-url.defaultZone=http://localhost:8761/eureka/
// spring.application.name=order-service

// Client with Load Balancer
@Service
public class OrderClient {
    @Autowired
    @LoadBalanced
    private RestTemplate restTemplate;

    public Order getOrder(String orderId) {
        // Uses service name — Eureka resolves to actual instance
        return restTemplate.getForObject(
            "http://order-service/api/orders/" + orderId, Order.class);
    }
}
```

---

## 11. Outbox Pattern

**Problem:** How to atomically update a database and publish a message to a broker — they are separate systems and cannot be in the same transaction.

**Solution:** Write the message to an "outbox" table in the same database transaction as the business data. A separate process polls the outbox and publishes to the message broker.

```
┌─────────────────────────────────────────┐
│              Service A                   │
│                                         │
│  BEGIN TRANSACTION                       │
│  1. INSERT INTO orders (...)            │
│  2. INSERT INTO outbox (message)        │
│  COMMIT                                  │
│                                         │
└──────────────────┬──────────────────────┘
                   │
          Outbox Poller (CDC)
                   │
                   ▼
          ┌────────────────┐
          │ Message Broker │
          │  (Kafka/RMQ)   │
          └────────────────┘
```

```java
@Transactional
public Order createOrder(OrderRequest request) {
    Order order = new Order(request);
    orderRepository.save(order);

    // Write event to outbox instead of publishing directly
    OutboxEvent event = new OutboxEvent()
        .setAggregateId(order.getId())
        .setAggregateType("Order")
        .setEventType("OrderCreated")
        .setPayload(objectMapper.writeValueAsString(order));
    outboxRepository.save(event);

    // Transactional outbox guarantees: if order is saved, event will be published
    return order;
}

// Separate poller publishes outbox events
@Component
public class OutboxPublisher {
    @Scheduled(fixedDelay = 1000)
    @Transactional
    public void publishPendingEvents() {
        List<OutboxEvent> events = outboxRepository
            .findByPublishedFalseOrderByCreatedAtAsc(PageRequest.of(0, 100));

        for (OutboxEvent event : events) {
            try {
                kafkaTemplate.send(event.getEventType(), event.getPayload());
                event.setPublished(true);
                outboxRepository.save(event);
            } catch (Exception e) {
                log.error("Failed to publish event: {}", event.getId(), e);
                break;  // Stop processing — will retry next cycle
            }
        }
    }
}
```

---

## 12. Retry Pattern with Exponential Backoff

```java
// Resilience4j Retry
@Retry(name = "paymentService", fallbackMethod = "processPaymentFallback")
public PaymentResult processPayment(PaymentRequest request) {
    return paymentClient.charge(request);
}

// Configuration
@Bean
public Retry paymentServiceRetry() {
    RetryConfig config = RetryConfig.custom()
        .maxAttempts(3)
        .waitDuration(Duration.ofMillis(500))
        .retryOnException(e -> e instanceof HttpServerErrorException
            || e instanceof SocketTimeoutException)
        .intervalBiFunction((attempt, Either<Throwable, Void> result) -> {
            // Exponential backoff with jitter
            long baseDelay = 500L;
            long maxDelay = 10000L;
            long delay = Math.min(maxDelay, baseDelay * (1L << attempt));
            long jitter = (long) (delay * 0.5 * Math.random());
            return Duration.ofMillis(delay + jitter);
        })
        .build();

    return Retry.of("paymentService", config);
}
```

---

## 13. Sharding Pattern

**Problem:** A single database cannot handle the data volume or throughput of a large-scale system.

**Solution:** Horizontally partition data across multiple database instances based on a shard key.

```
┌─────────────────────────────────────────────┐
│             Application Layer               │
│                                             │
│         Shard Router / Shard Key            │
│         (user_id % 3)                       │
│                                             │
│    ┌─────────┬──────────┬──────────┐        │
│    │         │          │          │        │
│    ▼         ▼          ▼          ▼        │
│ ┌──────┐ ┌──────┐  ┌──────┐              │
│ │Shard0│ │Shard1│  │Shard2│              │
│ │A-M   │ │N-S   │  │T-Z   │              │
│ └──────┘ └──────┘  └──────┘              │
└─────────────────────────────────────────────┘
```

---

## 14. Anti-Corruption Layer

**Problem:** A new microservice needs to integrate with a legacy system whose data model is messy or inconsistent.

**Solution:** Implement a translation layer that converts between the legacy model and the clean domain model of the new service.

```java
@Service
public class LegacyCustomerACL {
    private final LegacyCustomerClient legacyClient;

    // Translate legacy format to clean domain model
    public Customer getCustomer(String customerId) {
        LegacyCustomerRecord legacy = legacyClient.fetch(customerId);

        return Customer.builder()
            .id(legacy.getCustId())                          // custId → id
            .fullName(legacy.getFname() + " " + legacy.getLname())  // first+last → fullName
            .email(legacy.getEmailAddr())                    // emailAddr → email
            .status(mapStatus(legacy.getStatCd()))           // statCd → status (enum)
            .build();
    }

    private CustomerStatus mapStatus(String statusCode) {
        return switch (statusCode) {
            case "A", "ACT" -> CustomerStatus.ACTIVE;
            case "I", "INA" -> CustomerStatus.INACTIVE;
            case "S", "SUS" -> CustomerStatus.SUSPENDED;
            default -> CustomerStatus.UNKNOWN;
        };
    }
}
```

---

# Part III: System Design

## 1. URL Shortener (e.g., bit.ly)

### Requirements
- **Functional:** Given a long URL, generate a short URL; given a short URL, redirect to the original
- **Non-Functional:** High availability, low latency redirect, 100M+ URLs, 10:1 read:write ratio

### High-Level Architecture

```
┌──────────┐     ┌──────────────┐     ┌─────────────────┐
│  Client   │────►│  API Gateway  │────►│ URL Shortener   │
└──────────┘     │  (Load Balancer│     │    Service      │
                 └──────────────┘     └────────┬────────┘
                                               │
                            ┌──────────────────┼──────────────────┐
                            │                  │                  │
                     ┌──────▼──────┐   ┌───────▼──────┐   ┌─────▼──────┐
                     │   Write DB   │   │   Read Cache  │   │  Read DB   │
                     │  (MySQL/     │   │  (Redis)      │   │ (Read      │
                     │  PostgreSQL) │   │               │   │  Replica)  │
                     └──────────────┘   └───────────────┘   └────────────┘
```

### Key Design Decisions

**URL Encoding Strategy:**
```java
// Base62 encoding (0-9, a-z, A-Z = 62 chars)
// 7 characters = 62^7 = 3.5 trillion unique URLs
public class Base62Encoder {
    private static final String CHARSET =
        "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

    public static String encode(long id) {
        StringBuilder sb = new StringBuilder();
        while (id > 0) {
            sb.append(CHARSET.charAt((int) (id % 62)));
            id /= 62;
        }
        while (sb.length() < 7) sb.append('0');  // Pad to 7 chars
        return sb.reverse().toString();
    }

    public static long decode(String shortUrl) {
        long id = 0;
        for (char c : shortUrl.toCharArray()) {
            id = id * 62 + CHARSET.indexOf(c);
        }
        return id;
    }
}
```

**Service Implementation:**
```java
@Service
public class URLShortenerService {
    @Autowired
    private URLRepository urlRepository;
    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    private static final String CACHE_PREFIX = "url:";
    private static final String ID_KEY = "global:url:id";

    public String shortenURL(String longUrl) {
        // Check if already shortened (deduplication)
        String existing = urlRepository.findByLongUrl(longUrl);
        if (existing != null) return existing;

        // Generate unique ID (distributed ID generator)
        long id = generateDistributedId();
        String shortCode = Base62Encoder.encode(id);

        // Store mapping
        URLMapping mapping = new URLMapping(id, shortCode, longUrl);
        urlRepository.save(mapping);

        // Cache it
        redisTemplate.opsForValue().set(CACHE_PREFIX + shortCode, longUrl,
            Duration.ofHours(24));

        return shortCode;
    }

    public String getOriginalURL(String shortCode) {
        // Check cache first
        String cached = redisTemplate.opsForValue().get(CACHE_PREFIX + shortCode);
        if (cached != null) return cached;

        // Fallback to DB
        URLMapping mapping = urlRepository.findByShortCode(shortCode);
        if (mapping == null) throw new URLNotFoundException(shortCode);

        // Populate cache for next read
        redisTemplate.opsForValue().set(CACHE_PREFIX + shortCode,
            mapping.getLongUrl(), Duration.ofHours(24));

        return mapping.getLongUrl();
    }

    // Distributed unique ID using Snowflake
    private long generateDistributedId() {
        return snowflakeIdGenerator.nextId();
    }
}
```

**Redirect Flow (HTTP 301 vs 302):**
- **301 (Permanent):** Browser caches the redirect — no future requests hit the server. Good for performance, bad for analytics.
- **302 (Temporary):** Browser always hits the server first — enables click tracking and analytics. Most URL shorteners use 302.

**Interview Q:** *How do you handle distributed ID generation?*
**A:** Options include: (1) Database auto-increment (bottleneck), (2) UUID (no sort order, 128-bit), (3) Snowflake ID (64-bit, time-sorted, distributed), (4) Range-based pre-allocation (each server gets a range of IDs).

---

## 2. LRU Cache

### Requirements
- Fixed-size cache that evicts the least recently used item when full
- Both `get` and `put` must be O(1)

### Design

**Core Data Structure:** HashMap + Doubly Linked List

```
HashMap: key → Node reference
Doubly Linked List: maintains access order (MRU ←→ LRU)

┌──────────────────────────────────────────┐
│  Head (MRU)                         Tail (LRU) │
│    │                                   │    │
│    ▼                                   ▼    │
│  [Node3] ←→ [Node1] ←→ [Node5] ←→ [Node2] │
│    │          │          │          │     │
│    ▼          ▼          ▼          ▼     │
└──────────────────────────────────────────┘

After accessing Node5:
  [Node5] ←→ [Node3] ←→ [Node1] ←→ [Node2]
   Head(MRU)                         Tail(LRU)
```

**Implementation:**
```java
public class LRUCache<K, V> {
    private final int capacity;
    private final Map<K, Node<K, V>> cache;
    private final Node<K, V> head;  // Dummy head (MRU side)
    private final Node<K, V> tail;  // Dummy tail (LRU side)

    private static class Node<K, V> {
        K key;
        V value;
        Node<K, V> prev, next;

        Node() { this.key = null; this.value = null; }
        Node(K key, V value) { this.key = key; this.value = value; }
    }

    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new HashMap<>(capacity);

        // Initialize dummy head and tail
        head = new Node<>();
        tail = new Node<>();
        head.next = tail;
        tail.prev = head;
    }

    public V get(K key) {
        Node<K, V> node = cache.get(key);
        if (node == null) return null;

        // Move to front (most recently used)
        removeNode(node);
        addToFront(node);
        return node.value;
    }

    public void put(K key, V value) {
        Node<K, V> existing = cache.get(key);
        if (existing != null) {
            existing.value = value;
            removeNode(existing);
            addToFront(existing);
        } else {
            Node<K, V> newNode = new Node<>(key, value);
            cache.put(key, newNode);
            addToFront(newNode);

            if (cache.size() > capacity) {
                // Evict LRU (node before tail)
                Node<K, V> lru = tail.prev;
                removeNode(lru);
                cache.remove(lru.key);
            }
        }
    }

    private void addToFront(Node<K, V> node) {
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
    }

    private void removeNode(Node<K, V> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }
}
```

**Thread-Safe LRU Cache:**
```java
public class ThreadSafeLRUCache<K, V> {
    private final LRUCache<K, V> cache;
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();

    public ThreadSafeLRUCache(int capacity) {
        this.cache = new LRUCache<>(capacity);
    }

    public V get(K key) {
        lock.readLock().lock();
        try {
            return cache.get(key);
        } finally {
            lock.readLock().unlock();
        }
    }

    public void put(K key, V value) {
        lock.writeLock().lock();
        try {
            cache.put(key, value);
        } finally {
            lock.writeLock().unlock();
        }
    }
}

// Java standard library shortcut (for interviews):
// LinkedHashMap with access-order mode
public class LRUCacheSimple<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    public LRUCacheSimple(int capacity) {
        super(capacity, 0.75f, true);  // true = access-order
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;
    }
}
```

---

## 3. Rate Limiter

### Requirements
- Limit the number of requests a client can make within a time window
- Support different algorithms: Fixed Window, Sliding Window, Token Bucket, Leaky Bucket

### Architecture

```
┌──────────┐     ┌──────────────┐     ┌───────────────┐
│  Client   │────►│ Rate Limiter  │────►│   Service     │
└──────────┘     │  Middleware   │     └───────────────┘
                 └──────┬───────┘
                        │
                 ┌──────▼───────┐
                 │    Redis     │
                 │ (Counter/    │
                 │  Tokens)     │
                 └──────────────┘
```

### Implementation — Token Bucket (Most Common)

```
Token Bucket:
  ┌─────────────────────────────────────┐
  │  Bucket (capacity: 10 tokens)       │
  │  ○ ○ ○ ○ ○ ○ ○ _ _ _              │
  │  Refill rate: 2 tokens/second       │
  │                                     │
  │  Request arrives → token consumed   │
  │  No tokens → REJECT (429)           │
  └─────────────────────────────────────┘
```

```java
@Service
public class TokenBucketRateLimiter {
    @Autowired
    private StringRedisTemplate redisTemplate;

    private static final String SCRIPT =
        "local tokens_key = KEYS[1] .. ':tokens'\n" +
        "local timestamp_key = KEYS[1] .. ':timestamp'\n" +
        "local capacity = tonumber(ARGV[1])\n" +
        "local rate = tonumber(ARGV[2])\n" +
        "local requested = tonumber(ARGV[3])\n" +
        "local now = tonumber(ARGV[4])\n" +
        "\n" +
        "local tokens = tonumber(redis.call('get', tokens_key)) or capacity\n" +
        "local last_time = tonumber(redis.call('get', timestamp_key)) or now\n" +
        "\n" +
        "local elapsed = math.max(0, now - last_time)\n" +
        "local refill = elapsed * rate\n" +
        "tokens = math.min(capacity, tokens + refill)\n" +
        "\n" +
        "if tokens >= requested then\n" +
        "  tokens = tokens - requested\n" +
        "  redis.call('set', tokens_key, tokens)\n" +
        "  redis.call('set', timestamp_key, now)\n" +
        "  return 1\n" +
        "else\n" +
        "  redis.call('set', tokens_key, tokens)\n" +
        "  redis.call('set', timestamp_key, now)\n" +
        "  return 0\n" +
        "end\n";

    public boolean allowRequest(String clientId, int capacity, double refillRate, int requested) {
        String key = "rate_limit:" + clientId;
        long now = System.currentTimeMillis() / 1000.0;

        Long result = redisTemplate.execute(
            new DefaultRedisScript<>(SCRIPT, Long.class),
            List.of(key),
            String.valueOf(capacity),
            String.valueOf(refillRate),
            String.valueOf(requested),
            String.valueOf(now)
        );

        return result != null && result == 1;
    }
}
```

### Sliding Window Counter

```java
@Service
public class SlidingWindowRateLimiter {
    @Autowired
    private StringRedisTemplate redisTemplate;

    public boolean allowRequest(String clientId, int maxRequests, int windowSeconds) {
        long now = System.currentTimeMillis();
        String key = "sliding:" + clientId + ":" + (now / 1000 / windowSeconds);

        Long count = redisTemplate.opsForValue().increment(key);
        if (count != null && count == 1) {
            redisTemplate.expire(key, windowSeconds * 2, TimeUnit.SECONDS);
        }

        // Check previous window too for smooth sliding
        String prevKey = "sliding:" + clientId + ":" + ((now / 1000 / windowSeconds) - 1);
        Long prevCount = Long.parseLong(
            redisTemplate.opsForValue().get(prevKey) == null ? "0" :
            redisTemplate.opsForValue().get(prevKey));

        double elapsedRatio = (now % (windowSeconds * 1000)) / (double) (windowSeconds * 1000);
        double estimatedCount = prevCount * (1 - elapsedRatio) + count;

        return estimatedCount <= maxRequests;
    }
}
```

**Interview Q:** *Compare rate limiting algorithms: Fixed Window vs Sliding Window vs Token Bucket vs Leaky Bucket?*
**A:**
- **Fixed Window:** Simple but has burst problem at window boundaries (2x traffic at boundary)
- **Sliding Window:** Smooths the boundary problem, slightly more complex
- **Token Bucket:** Allows controlled bursts up to bucket capacity, good for APIs (most production systems use this)
- **Leaky Bucket:** Smooths traffic to a constant rate, no bursts allowed, good for logging systems

---

## 4. Design a Chat System (e.g., WhatsApp/Slack)

### Requirements
- One-on-one and group chat
- Message delivery, read receipts, online status
- Low latency, high availability, message ordering

### Architecture

```
┌──────────┐                         ┌──────────┐
│  Client A │◄──── WebSocket ────►   │  Client B │
└────┬─────┘                         └─────┬────┘
     │                                     │
     ▼                                     ▼
┌──────────────────────────────────────────────────┐
│              Load Balancer (Sticky Sessions)      │
└──────────────────────┬───────────────────────────┘
                       │
              ┌────────▼────────┐
              │  Chat Service   │
              │  (WebSocket     │
              │   Handler)      │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
   ┌──────▼──────┐ ┌──▼────────┐ ┌▼──────────┐
   │Message Queue│ │  Redis    │ │  Database  │
   │ (Kafka)     │ │ (Online   │ │(Cassandra/ │
   │             │ │  Status,  │ │ DynamoDB)  │
   │             │ │  Pub/Sub) │ │            │
   └─────────────┘ └───────────┘ └────────────┘
```

### Key Components

```java
// WebSocket Handler
@Component
public class ChatWebSocketHandler extends TextWebSocketHandler {
    // userId → WebSocket session mapping
    private final ConcurrentHashMap<String, WebSocketSession> sessions =
        new ConcurrentHashMap<>();

    @Autowired
    private KafkaTemplate<String, ChatMessage> kafkaTemplate;

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        String userId = extractUserId(session);
        sessions.put(userId, session);
        publishOnlineStatus(userId, true);
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message)
            throws Exception {
        ChatMessage chatMsg = objectMapper.readValue(message.getPayload(), ChatMessage.class);

        // Publish to Kafka for persistence and delivery
        kafkaTemplate.send("chat-messages",
            chatMsg.getRecipientId(), chatMsg);
    }

    @KafkaListener(topics = "chat-messages", groupId = "chat-delivery")
    public void deliverMessage(ChatMessage message) {
        WebSocketSession recipientSession = sessions.get(message.getRecipientId());
        if (recipientSession != null && recipientSession.isOpen()) {
            recipientSession.sendMessage(
                new TextMessage(objectMapper.writeValueAsString(message)));
            // Send delivery receipt
            message.setStatus(MessageStatus.DELIVERED);
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        String userId = extractUserId(session);
        sessions.remove(userId);
        publishOnlineStatus(userId, false);
    }
}
```

**Message Ordering Guarantee:**
```java
// Use Kafka partitioning by conversation ID for ordering
kafkaTemplate.send(
    new ProducerRecord<>(
        "chat-messages",
        conversationId,  // Partition key — same conversation → same partition → ordered
        chatMessage
    )
);
```

---

## 5. Design a News Feed System (e.g., Facebook/Twitter)

### Requirements
- Users can post content
- Users see a feed of posts from people they follow
- Feed must be personalized and sorted by relevance/recency

### Two Core Approaches

**Approach 1: Pull (Fan-out on Read)**
```
When user requests feed:
  1. Get list of followed user IDs
  2. Fetch recent posts from each followed user
  3. Merge and sort
  4. Return feed

Pros: No wasted work for inactive users, simple writes
Cons: Slow reads (multiple DB queries), doesn't scale for large follow lists
```

**Approach 2: Push (Fan-out on Write)**
```
When user creates a post:
  1. Write post to Post DB
  2. Get list of followers
  3. Push post to each follower's feed (cache)

When user requests feed:
  1. Simply read from pre-computed feed cache

Pros: Fast reads (pre-computed), good for active readers
Cons: Slow writes for users with millions of followers, wasted work for inactive followers
```

**Hybrid Approach (Best for Scale):**
```java
@Service
public class FeedService {
    @Autowired private PostRepository postRepository;
    @Autowired private RedisTemplate<String, Post> redisTemplate;
    @Autowired private FollowService followService;

    private static final int FEED_SIZE = 1000;
    private static final int CELEBRITY_THRESHOLD = 10000;

    // When a user posts — fan-out on write
    public void onPostCreated(Post post) {
        // Save to post DB
        postRepository.save(post);

        List<String> followers = followService.getFollowers(post.getAuthorId());

        if (followers.size() > CELEBRITY_THRESHOLD) {
            // Celebrity: don't fan-out, mark for pull
            redisTemplate.opsForSet().add("celebrity_users", post.getAuthorId());
        } else {
            // Regular user: push to followers' feeds
            for (String followerId : followers) {
                String feedKey = "feed:" + followerId;
                redisTemplate.opsForList().leftPush(feedKey, post);
                redisTemplate.opsForList().trim(feedKey, 0, FEED_SIZE - 1);
            }
        }
    }

    // When user requests feed
    public List<Post> getFeed(String userId) {
        // Get pre-computed feed (push)
        List<Post> feed = redisTemplate.opsForList()
            .range("feed:" + userId, 0, 50);

        // Merge with celebrity posts (pull)
        Set<String> celebrityFollows = redisTemplate.opsForSet()
            .intersect("following:" + userId, "celebrity_users");

        if (celebrityFollows != null && !celebrityFollows.isEmpty()) {
            List<Post> celebrityPosts = postRepository
                .findRecentPostsByAuthors(celebrityFollows, PageRequest.of(0, 50));
            feed = mergeAndSort(feed, celebrityPosts);
        }

        return feed;
    }
}
```

---

## 6. Design a Notification System

### Architecture

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│Order Svc │  │Chat Svc  │  │Social Svc│
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┼─────────────┘
                   │
            ┌──────▼──────┐
            │Notification │
            │   Service   │
            │             │
            │ - Dedup     │
            │ - Rate Limit│
            │ - Template  │
            │ - Priority  │
            └──────┬──────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
┌────▼────┐  ┌────▼────┐  ┌────▼────┐
│  Email  │  │   SMS   │  │  Push   │
│Provider │  │Provider │  │Provider │
│(SES)    │  │(Twilio) │  │(FCM)    │
└─────────┘  └─────────┘  └─────────┘
```

```java
@Service
public class NotificationService {
    @Autowired private NotificationRepository repository;
    @Autowired private KafkaTemplate<String, NotificationEvent> kafkaTemplate;

    // Priority queue processing
    public void sendNotification(NotificationRequest request) {
        // Deduplication
        String dedupKey = request.getUserId() + ":" + request.getType() + ":" + request.getEntityId();
        if (repository.existsByDedupKey(dedupKey)) return;

        // Rate limiting — don't spam users
        if (isRateLimited(request.getUserId(), request.getType())) return;

        // Create notification
        Notification notification = Notification.builder()
            .userId(request.getUserId())
            .type(request.getType())
            .title(renderTemplate(request.getTemplateId(), request.getParams()))
            .priority(request.getPriority())
            .dedupKey(dedupKey)
            .build();

        repository.save(notification);

        // Publish to appropriate channel
        for (String channel : request.getChannels()) {
            kafkaTemplate.send("notification-" + channel,
                new NotificationEvent(notification, channel));
        }
    }
}
```

---

## 7. Design a Web Crawler

### Architecture

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Seed URLs   │────►│  URL Frontier   │────►│   Fetcher    │
│              │     │  (Priority Queue│     │  (Workers)   │
│              │     │   + Dedup)      │     │              │
└──────────────┘     └─────────────────┘     └──────┬───────┘
                            ▲                        │
                            │                        ▼
                     ┌──────┴───────┐        ┌──────────────┐
                     │  URL Extract │◄───────│   Parser     │
                     │  (from HTML) │        │  (HTML →     │
                     └──────────────┘        │   Content)   │
                                             └──────┬───────┘
                                                    │
                                             ┌──────▼───────┐
                                             │   Storage    │
                                             │ (Index/DB)   │
                                             └──────────────┘
```

```java
@Service
public class WebCrawler {
    private final PriorityBlockingQueue<URL> urlFrontier = new PriorityBlockingQueue<>(
        1000, Comparator.comparingInt(URL::getPriority).reversed()
    );
    private final Set<String> visited = ConcurrentHashMap.newKeySet();
    private final ExecutorService executor;

    public WebCrawler(int numWorkers) {
        this.executor = Executors.newFixedThreadPool(numWorkers);
    }

    public void start(List<String> seedUrls) {
        seedUrls.forEach(url -> urlFrontier.add(new URL(url, 0)));

        while (!urlFrontier.isEmpty()) {
            URL url = urlFrontier.poll(1, TimeUnit.SECONDS);
            if (url == null || !visited.add(url.getNormalized())) continue;

            executor.submit(() -> crawl(url));
        }
    }

    private void crawl(URL url) {
        try {
            // Respect robots.txt and rate limiting
            if (!robotsChecker.isAllowed(url)) return;
            Thread.sleep(politenessDelay);

            // Fetch
            String html = httpClient.fetch(url);

            // Parse
            ParsedPage page = parser.parse(html);

            // Store
            indexService.index(page);

            // Extract new URLs
            for (String newUrl : page.getLinks()) {
                String normalized = normalize(newUrl);
                if (!visited.contains(normalized)) {
                    urlFrontier.add(new URL(normalized, url.getDepth() + 1));
                }
            }
        } catch (Exception e) {
            urlFrontier.add(url);  // Re-queue on failure
        }
    }
}
```

---

## 8. Design a Distributed Cache

### Architecture

```
┌──────────┐     ┌─────────────────────────────────────────┐
│  Client   │────►│         Consistent Hashing Ring        │
└──────────┘     │                                         │
                 │   Node1    Node2    Node3    Node4      │
                 │  (0-25%)  (25-50%) (50-75%) (75-100%)  │
                 │                                         │
                 │   Virtual Nodes for better distribution │
                 └─────────────────────────────────────────┘
```

**Consistent Hashing Implementation:**
```java
public class ConsistentHashing {
    private final TreeMap<Integer, String> ring = new TreeMap<>();
    private final int virtualNodes;
    private final MessageDigest md5;

    public ConsistentHashing(List<String> nodes, int virtualNodes) {
        this.virtualNodes = virtualNodes;
        try {
            this.md5 = MessageDigest.getInstance("MD5");
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

        for (String node : nodes) {
            addNode(node);
        }
    }

    public void addNode(String node) {
        for (int i = 0; i < virtualNodes; i++) {
            int hash = hash(node + ":" + i);
            ring.put(hash, node);
        }
    }

    public void removeNode(String node) {
        for (int i = 0; i < virtualNodes; i++) {
            int hash = hash(node + ":" + i);
            ring.remove(hash);
        }
    }

    public String getNode(String key) {
        if (ring.isEmpty()) throw new IllegalStateException("No nodes available");

        int hash = hash(key);
        Map.Entry<Integer, String> entry = ring.ceilingEntry(hash);
        if (entry == null) entry = ring.firstEntry();  // Wrap around
        return entry.getValue();
    }

    private int hash(String key) {
        byte[] digest = md5.digest(key.getBytes());
        return ((digest[3] & 0xFF) << 24) | ((digest[2] & 0xFF) << 16) |
               ((digest[1] & 0xFF) << 8) | (digest[0] & 0xFF);
    }
}
```

---

## 9. Design an Object Storage System (e.g., S3)

### Architecture

```
┌──────────┐     ┌──────────────┐     ┌───────────────┐
│  Client   │────►│  API Service │────►│  Metadata DB  │
│          │     │  (Upload/    │     │  (file name,  │
│          │     │   Download)  │     │   size, nodes)│
└──────────┘     └──────┬───────┘     └───────────────┘
                        │
              ┌─────────┼─────────┐
              │         │         │
         ┌────▼───┐ ┌──▼───┐ ┌──▼───┐
         │Storage  │ │Storage│ │Storage│
         │Node 1  │ │Node 2 │ │Node 3│
         │(Data)  │ │(Data) │ │(Data)│
         └────────┘ └───────┘ └──────┘
         (Replication factor = 3)
```

**Key Design Choices:**
- **Metadata:** Store in a distributed database (Cassandra/DynamoDB)
- **Data:** Store on local disks with replication across nodes
- **Upload:** Use presigned URLs for direct upload to storage nodes (bypass API service)
- **Download:** API service returns presigned URL for direct download
- **Erasure Coding:** For large objects, split into data + parity chunks

---

## 10. Design a Search Autocomplete System

### Trie-Based Approach

```
           root
          / | \
         a  b  c
        /   |   \
       p    o    a
      /     |     \
     p      o      t
    / \     |       \
   l   r    k        (cat: 5000)
  (apple: 1000) (book: 3000)
   (appr: 800)
```

```java
public class AutoCompleteSystem {
    private static class TrieNode {
        Map<Character, TrieNode> children = new HashMap<>();
        Map<String, Integer> frequencies = new HashMap<>();  // word → frequency
    }

    private final TrieNode root = new TrieNode();

    // Insert a search term
    public void insert(String term, int frequency) {
        TrieNode node = root;
        for (char c : term.toCharArray()) {
            node.children.computeIfAbsent(c, k -> new TrieNode());
            node = node.children.get(c);
            node.frequencies.merge(term, frequency, Integer::sum);
        }
    }

    // Get top-K suggestions for a prefix
    public List<String> suggest(String prefix, int k) {
        TrieNode node = root;
        for (char c : prefix.toCharArray()) {
            node = node.children.get(c);
            if (node == null) return Collections.emptyList();
        }

        return node.frequencies.entrySet().stream()
            .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
            .limit(k)
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
    }
}
```

**Production System at Scale:**
- Use Redis sorted sets for top-K suggestions per prefix
- Sharding: distribute prefix ranges across Redis nodes
- Update frequencies asynchronously from search logs
- Cache popular prefixes at the application layer

---

## 11. Design a Distributed ID Generator (Snowflake)

```
┌─────────────────────────────────────────────────────┐
│                  64-bit Snowflake ID                 │
├──────┬──────────────┬─────────────┬────────────────┤
│  1   │     41       │     10      │      12        │
│ sign │  timestamp   │  machine ID │   sequence     │
│ bit  │  (ms since   │  (datacenter│   number       │
│      │   epoch)     │  + worker)  │   (per ms)     │
└──────┴──────────────┴─────────────┴────────────────┘
  0/1    ~69 years      1024 nodes   4096 IDs/ms
```

```java
public class SnowflakeIdGenerator {
    private static final long EPOCH = 1704067200000L;  // Jan 1, 2024
    private static final long MACHINE_ID_BITS = 10L;
    private static final long SEQUENCE_BITS = 12L;

    private static final long MAX_MACHINE_ID = ~(-1L << MACHINE_ID_BITS);  // 1023
    private static final long MAX_SEQUENCE = ~(-1L << SEQUENCE_BITS);      // 4095

    private static final long MACHINE_ID_SHIFT = SEQUENCE_BITS;
    private static final long TIMESTAMP_SHIFT = SEQUENCE_BITS + MACHINE_ID_BITS;

    private final long machineId;
    private long lastTimestamp = -1L;
    private long sequence = 0L;

    public SnowflakeIdGenerator(long machineId) {
        if (machineId < 0 || machineId > MAX_MACHINE_ID) {
            throw new IllegalArgumentException("Machine ID out of range");
        }
        this.machineId = machineId;
    }

    public synchronized long nextId() {
        long timestamp = System.currentTimeMillis();

        if (timestamp < lastTimestamp) {
            throw new RuntimeException("Clock moved backwards!");
        }

        if (timestamp == lastTimestamp) {
            sequence = (sequence + 1) & MAX_SEQUENCE;
            if (sequence == 0) {
                timestamp = waitNextMillis(lastTimestamp);
            }
        } else {
            sequence = 0;
        }

        lastTimestamp = timestamp;

        return ((timestamp - EPOCH) << TIMESTAMP_SHIFT)
             | (machineId << MACHINE_ID_SHIFT)
             | sequence;
    }

    private long waitNextMillis(long lastTimestamp) {
        long timestamp = System.currentTimeMillis();
        while (timestamp <= lastTimestamp) {
            timestamp = System.currentTimeMillis();
        }
        return timestamp;
    }
}
```

---

## 12. Design a Key-Value Store (e.g., DynamoDB)

### Architecture

```
┌──────────────────────────────────────────────┐
│              Dynamo-Style Architecture        │
│                                              │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐    │
│  │Node A│  │Node B│  │Node C│  │Node D│    │
│  │Coord │  │      │  │      │  │      │    │
│  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘    │
│     │         │         │         │         │
│     └─────────┴────┬────┴─────────┘         │
│                    │                         │
│         Consistent Hashing Ring              │
│         Replication Factor N=3               │
│         Quorum: R=2, W=2 (strong consistency)│
│         or R=1, W=1 (eventual consistency)   │
└──────────────────────────────────────────────┘
```

**Write Flow (Quorum-Based):**
1. Coordinator receives write request
2. Coordinator generates vector clock
3. Writes to N nodes (replication factor)
4. Waits for W acknowledgments (write quorum)
5. Returns success to client

**Read Flow:**
1. Coordinator receives read request
2. Reads from N nodes
3. Waits for R responses (read quorum)
4. If conflict: return all versions (or resolve by vector clock)
5. Returns latest value

**Read/Write Consistency:**
- **Strong:** W + R > N (e.g., N=3, W=2, R=2)
- **Eventual:** W + R <= N (e.g., N=3, W=1, R=1)

---

# Part IV: Company-Wise Interview Questions & Answers

## Google

### Q1: Design Google Drive
**Key Points:**
- Block-level storage (split files into 4MB blocks)
- Metadata service for file hierarchy and permissions
- Conflict resolution using vector clocks
- Delta sync for bandwidth optimization
- CDN for shared file downloads

### Q2: Design YouTube
**Key Points:**
- Video upload → transcoding pipeline (multiple resolutions)
- Object storage for video files (S3/GCS)
- CDN for video delivery (edge caching)
- Separate metadata DB (sharded by video ID)
- Adaptive bitrate streaming (HLS/DASH)

### Q3: Design Google Maps
**Key Points:**
- Quadtree for map tile indexing
- Dijkstra/A* for routing with pre-computed paths
- Geohashing for nearby search
- Tile server with CDN caching
- Real-time traffic overlay via WebSocket

### Q4: How would you handle 10M concurrent WebSocket connections?
**Answer:**
```
Architecture:
- Load balancer with sticky sessions (or consistent hashing)
- Multiple WebSocket gateway servers (each handles ~100K connections)
- Message broker (Kafka) for inter-server communication
- Redis pub/sub for presence/status

JVM Tuning:
- -Xmx4g -Xms4g (fixed heap)
- -XX:+UseG1GC (low pause GC)
- Epoll (Linux) for efficient I/O multiplexing
- Off-heap buffers for large message queues

Connection Management:
- Netty for async I/O (non-blocking)
- Heartbeat every 30s for connection keep-alive
- Connection draining on server shutdown
```

---

## Amazon

### Q1: Design Amazon's Product Catalog
**Key Points:**
- Write: DynamoDB (high write throughput)
- Read: Elasticsearch (full-text search, filters)
- Cache: Redis (hot products)
- Image: S3 + CloudFront CDN
- Search: Elasticsearch with custom analyzers

### Q2: Design Amazon's Order Processing Pipeline
**Key Points:**
- Saga pattern for distributed transactions
- Event-driven: Order → Payment → Inventory → Shipping
- Outbox pattern for reliable event publishing
- Dead Letter Queue for failed messages
- Idempotent consumers for exactly-once processing

```java
// Idempotent consumer pattern
@Service
public class IdempotentOrderProcessor {
    @Autowired
    private ProcessedEventRepository processedEventRepo;
    @Autowired
    private OrderService orderService;

    @Transactional
    public void processOrderEvent(OrderEvent event) {
        // Check if already processed
        if (processedEventRepo.existsById(event.getEventId())) {
            log.info("Duplicate event ignored: {}", event.getEventId());
            return;  // Idempotent — safe to reprocess
        }

        // Process the event
        orderService.updateOrder(event);

        // Mark as processed
        processedEventRepo.save(new ProcessedEvent(event.getEventId(), Instant.now()));
    }
}
```

### Q3: How does Amazon achieve high availability (99.99%)?
**Answer:**
- Multi-AZ deployment (each AZ is an isolated data center)
- Auto-scaling groups with health checks
- Circuit breakers at every service boundary
- Graceful degradation (show cached data when DB is slow)
- Chaos engineering (GameDay exercises, failure injection)
- Blue-green and canary deployments

---

## Meta (Facebook)

### Q1: Design Facebook's News Feed
*(Covered in Part III, Section 5)*

### Q2: Design Facebook Messenger
**Key Points:**
- WebSocket for real-time delivery
- Kafka partitioned by conversation ID for ordering
- Cassandra for message storage (write-optimized)
- Long-polling fallback for restricted networks
- End-to-end encryption with Signal Protocol

### Q3: How does Facebook handle billions of photo uploads?
**Answer:**
- Haystack architecture: optimized for write-once, read-many
- Photo upload → thumbnail generation (multiple sizes)
- Multi-tier caching: CDN → Haystack Cache → Haystack Store
- Warm/cold storage tiering (old photos → cheaper storage)
- Geo-replicated storage for low-latency access globally

---

## Microsoft

### Q1: Design Azure Service Bus / Message Queue
**Key Points:**
- Partitioned queues for throughput
- At-least-once delivery with dedup on consumer
- Dead-letter queue for poison messages
- Sessions for message ordering
- Replay capability for debugging

### Q2: Design Microsoft Teams
**Key Points:**
- Signaling: WebSocket for call setup
- Media: WebRTC for P2P, SFU for group calls
- Chat: Similar to messenger (WebSocket + Kafka)
- Presence: Redis pub/sub with TTL
- File sharing: OneDrive integration with presigned URLs

---

## Netflix

### Q1: Design Netflix's Video Streaming
**Key Points:**
- Origin server → Transcoding → CDN edge nodes
- Adaptive bitrate: encode at multiple resolutions/bitrates
- A/B testing infrastructure for UI experiments
- Chaos Monkey: randomly kill instances to test resilience
- Hystrix/Resilience4j for fallbacks

### Q2: Design Netflix's Recommendation System
**Key Points:**
- Collaborative filtering: "Users who watched X also watched Y"
- Content-based: genre, actors, director similarity
- Real-time: trending, recently added
- Model training: Spark MLlib on viewing history
- Serving: Pre-computed recommendations + real-time adjustments

---

## Flipkart (India)

### Q1: Design a Flash Sale System
**Key Points:**
- **Challenge:** 100x traffic spike for limited inventory
- Pre-warm caches with product and inventory data
- Queue-based ordering (don't hit DB directly)
- Distributed locks for inventory reservation
- Rate limiting at API gateway
- Static content offloaded to CDN

```java
// Flash sale with distributed lock
@Service
public class FlashSaleService {
    @Autowired
    private RedissonClient redisson;
    @Autowired
    private InventoryService inventoryService;

    public SaleResult purchase(String userId, String productId) {
        String lockKey = "flash_sale_lock:" + productId;
        RLock lock = redisson.getLock(lockKey);

        try {
            // Try to acquire lock with timeout
            if (!lock.tryLock(5, 10, TimeUnit.SECONDS)) {
                return SaleResult.busy();
            }

            // Check inventory
            if (!inventoryService.decrementStock(productId)) {
                return SaleResult.soldOut();
            }

            // Process order
            Order order = orderService.createOrder(userId, productId);
            return SaleResult.success(order);

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return SaleResult.error();
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }
}
```

### Q2: Design a Payment System
**Key Points:**
- Idempotency keys for all operations
- Saga pattern for multi-step payment flow
- Circuit breaker for third-party payment gateway
- Reconciliation service for settlement
- PCI DSS compliance for card data

---

## Uber

### Q1: Design Uber's Ride Matching
**Key Points:**
- Geohashing for driver/rider proximity matching
- WebSocket for real-time driver location updates
- Dispatch service with nearest-driver algorithm
- Surge pricing: dynamic based on supply/demand ratio
- Trip lifecycle: Request → Match → Pickup → Trip → Complete

```
┌─────────────────────────────────────────┐
│           Ride Matching Flow            │
│                                         │
│  Rider Request → Dispatch Service       │
│       │                                 │
│       ▼                                 │
│  Geohash Lookup (nearby drivers)        │
│       │                                 │
│       ▼                                 │
│  Filter: available, within radius       │
│       │                                 │
│       ▼                                 │
│  Rank: distance, rating, ETA           │
│       │                                 │
│       ▼                                 │
│  Send offer to top-N drivers            │
│       │                                 │
│       ▼                                 │
│  First accept wins (or timeout)         │
└─────────────────────────────────────────┘
```

---

## Common Architect-Level Questions (All Companies)

### Q: How do you handle schema evolution in microservices?
```java
// Backward-compatible schema evolution using Avro
// Old consumer can read new schema (ignores new fields)
// New consumer can read old schema (uses defaults)

// Approach 1: Schema Registry (Confluent/Kafka)
@Configuration
public class KafkaAvroConfig {
    @Bean
    public KafkaTemplate<String, GenericRecord> avroKafkaTemplate() {
        Map<String, Object> props = Map.of(
            "schema.registry.url", "http://localhost:8081",
            "value.subject.name.strategy",
                "io.confluent.kafka.serializers.subject.RecordNameStrategy"
        );
        ProducerFactory<String, GenericRecord> factory =
            new DefaultKafkaProducerFactory<>(props);
        return new KafkaTemplate<>(factory);
    }
}

// Approach 2: API Versioning
@RestController
@RequestMapping("/api/v2/orders")
public class OrderControllerV2 {
    // V2 adds shipping tracking field
    // V1 controller still exists at /api/v1/orders
}
```

### Q: How do you ensure data consistency across microservices?
**Answer:**
1. **Saga Pattern** — orchestrate distributed transactions with compensations
2. **Outbox Pattern** — guarantee at-least-once event delivery
3. **Idempotent Consumers** — handle duplicate messages safely
4. **Eventual Consistency** — accept temporary inconsistency, converge over time
5. **CQRS** — separate read/write models for consistency boundaries

### Q: How do you design for observability?
**Answer:**
```
Three Pillars of Observability:

1. LOGS (Structured, Centralized)
   - ELK Stack or Loki
   - Correlation IDs across services
   - Structured logging (JSON format)
   - Log levels: ERROR > WARN > INFO > DEBUG

2. METRICS (Time-Series, Alertable)
   - Prometheus + Grafana
   - RED method: Rate, Errors, Duration
   - USE method: Utilization, Saturation, Errors
   - SLIs/SLOs/SLAs

3. TRACES (Distributed Request Tracing)
   - Jaeger or Zipkin
   - OpenTelemetry instrumentation
   - Span: single operation
   - Trace: complete request flow across services

Implementation:
   @Bean
   public ObservedAspect observedAspect(ObservationRegistry registry) {
       return new ObservedAspect(registry);
       // Auto-instruments Spring components with metrics + traces
   }
```

### Q: How do you handle secrets management in microservices?
```java
// HashiCorp Vault integration
@Configuration
public class VaultConfig {
    @Bean
    public VaultTemplate vaultTemplate() {
        return new VaultTemplate(
            new VaultEndpoint(),
            new TokenAuthentication("vault-token"));
    }
}

// Spring Cloud Vault
// application.yml:
// spring.cloud.vault.uri=https://vault.example.com
// spring.cloud.vault.token=${VAULT_TOKEN}

// Inject secrets as properties
@Value("${database.password}")
private String dbPassword;  // Fetched from Vault at runtime
```

### Q: Explain CAP Theorem with real-world examples
```
CAP Theorem: You can have at most 2 of 3:

1. Consistency — All nodes see the same data simultaneously
2. Availability — Every request receives a response (not error)
3. Partition Tolerance — System continues despite network failures

In distributed systems, partition is inevitable, so the real choice is:

CP (Consistency + Partition Tolerance):
  - ZooKeeper, etcd, HBase
  - When partition occurs, reject some requests to maintain consistency
  - Use case: financial transactions, leader election

AP (Availability + Partition Tolerance):
  - Cassandra, DynamoDB (eventual consistency mode), CouchDB
  - When partition occurs, serve stale data but stay available
  - Use case: social media feeds, shopping carts

Note: Modern systems allow tuning per-operation:
  - DynamoDB: strongly consistent read OR eventually consistent read
  - Cassandra: QUORUM consistency level per query
```

### Q: What is the difference between ACID and BASE?
```
ACID (Traditional RDBMS):
  Atomicity    — All or nothing
  Consistency  — Valid state transitions only
  Isolation    — Concurrent transactions don't interfere
  Durability   — Committed data is permanent

BASE (NoSQL/Distributed):
  Basically Available  — System responds (may be stale)
  Soft State          — State may change without input (replication lag)
  Eventually Consistent — Given enough time, all replicas converge

Trade-off:
  ACID → Strong consistency, lower availability under partitions
  BASE → High availability, accept temporary inconsistency

When to choose which:
  ACID: Banking, inventory management, booking systems
  BASE: Social media, analytics, recommendation systems
```

### Q: How do you design for horizontal scaling?
**Answer:**
1. **Stateless Services** — No server-side sessions; store state externally (Redis, DB)
2. **Database Sharding** — Partition data by shard key across multiple DB instances
3. **Caching Layers** — Redis/Memcached to reduce DB load
4. **Async Processing** — Message queues to decouple and buffer requests
5. **Auto-Scaling** — Scale out/in based on metrics (CPU, request rate, queue depth)
6. **Load Balancing** — Distribute traffic across instances (round-robin, least connections)
7. **CDN** — Serve static content from edge locations

### Q: Explain the difference between strong consistency and eventual consistency
```java
// Strong consistency (linearizability)
// After a write completes, all subsequent reads see the new value
// Implementation: Distributed lock + quorum reads/writes

// Example: Bank account transfer
@Transactional
public void transfer(String from, String to, double amount) {
    accountRepo.debit(from, amount);  // Must be atomic
    accountRepo.credit(to, amount);   // Must be atomic
    // Both operations succeed or both fail — no intermediate state visible
}

// Eventual consistency
// After a write, reads may see stale data, but eventually converge
// Implementation: Async replication, last-write-wins

// Example: Social media follower count
public int getFollowerCount(String userId) {
    // May return slightly stale count — acceptable
    return cache.get("followers:" + userId);
    // Background sync updates cache periodically
}
```

### Q: How would you migrate a monolith to microservices?
**Answer (Strangler Fig Pattern with practical steps):**
1. **Assessment** — Identify bounded contexts, domain boundaries
2. **Strangle gradually** — Start with low-risk, standalone services
3. **Anti-Corruption Layer** — Protect new services from legacy model
4. **Data migration** — Duplicate data initially, sync via events, then cut over
5. **Feature flags** — Switch between monolith and microservice implementations
6. **Monitor** — Compare behavior of old vs new during migration

---

# Part V: Interview Tips & Strategies

## 1. System Design Interview Framework (RESHADED)

Use this framework to structure your system design interview:

| Step | Description | Key Questions |
|------|-------------|---------------|
| **R**equirements | Clarify functional & non-functional | "What's the scale? What's the read:write ratio?" |
| **E**stimation | Back-of-envelope calculations | QPS, storage, bandwidth, memory |
| **S**torage Schema | Define data models & storage choices | SQL vs NoSQL? Sharding key? |
| **H**igh-Level Design | Draw the architecture diagram | Components, data flow |
| **A**PI Design | Define interfaces | REST endpoints, events |
| **D**eep Dive | Explore 2-3 components in depth | "How would you handle X failure?" |
| **E**dge Cases | Discuss failures, limits, security | "What if DB is down? Scale 10x?" |
| **D**istinctions | Compare alternatives & justify choices | "Why Kafka over RabbitMQ?" |

## 2. Common Estimation Cheat Sheet

| Metric | Value |
|--------|-------|
| Latency: L1 cache | 1 ns |
| Latency: L2 cache | 5 ns |
| Latency: Main memory | 100 ns |
| Latency: SSD random read | 100 μs |
| Latency: HDD seek | 10 ms |
| Latency: Network same DC | 0.5 ms |
| Latency: Network cross-region | 50-150 ms |
| Bandwidth: 1 Gbps | ~125 MB/s |
| QPS per web server | ~1,000-5,000 |
| QPS per DB (read) | ~10,000 |
| QPS per DB (write) | ~1,000-5,000 |

## 3. Architecture Decision Framework

When making architectural choices, always consider:

1. **Business Requirements** — What problem are we solving?
2. **Scale** — Current and projected (users, data, traffic)
3. **Latency** — Real-time vs near-real-time vs batch
4. **Consistency** — Strong vs eventual
5. **Availability** — 99.9% vs 99.99% vs 99.999%
6. **Cost** — Infrastructure, team expertise, operational overhead
7. **Team** — Skills, size, velocity
8. **Trade-offs** — Every decision has pros and cons; articulate them

## 4. Key Java Architecture Concepts to Master

### JVM Internals
- **Memory Model:** Heap (Young/Old), Metaspace, Stack, Direct Buffer
- **GC Algorithms:** G1, ZGC, Shenandoah — when to choose which
- **JIT Compilation:** C1 (client), C2 (server), tiered compilation
- **Thread Model:** Platform threads vs Virtual threads (Project Loom/Java 21+)

```java
// Virtual Threads (Java 21+) — lightweight, millions of concurrent tasks
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<String>> futures = urls.stream()
        .map(url -> executor.submit(() -> httpClient.fetch(url)))
        .toList();

    for (Future<String> f : futures) {
        System.out.println(f.get());
    }
}
// Each virtual thread uses ~1KB vs ~1MB for platform threads
```

### Spring Boot 3+ Architecture
- **Auto-Configuration** — How `@EnableAutoConfiguration` works via `spring.factories` / `AutoConfiguration.imports`
- **Bean Lifecycle** — Instantiation → Population → Initialization → Usage → Destruction
- **AOP** — JDK dynamic proxy vs CGLIB proxy
- **Reactive Stack** — WebFlux + Netty for non-blocking I/O

### Database Design
- **Indexing** — B+ tree, covering index, composite index, index-only scan
- **Partitioning** — Range, Hash, List partitioning strategies
- **Connection Pooling** — HikariCP configuration for production
- **Read Replicas** — Replication lag handling, stale read mitigation

```java
// HikariCP production configuration
@Bean
public DataSource dataSource() {
    HikariConfig config = new HikariConfig();
    config.setJdbcUrl("jdbc:postgresql://db:5432/mydb");
    config.setMaximumPoolSize(50);          // CPU cores * 2 + effective spindles
    config.setMinimumIdle(10);
    config.setConnectionTimeout(30000);     // 30s wait for connection
    config.setIdleTimeout(600000);          // 10min idle timeout
    config.setMaxLifetime(1800000);         // 30min max lifetime
    config.setLeakDetectionThreshold(60000);// 1min leak detection
    config.addDataSourceProperty("preparedStatementCacheSize", 256);
    config.addDataSourceProperty("preparedStatementCacheSqlLimit", 2048);
    return new HikariDataSource(config);
}
```

## 5. Behavioral Interview Tips

### STAR Method
- **S**ituation: Describe the context
- **T**ask: What was your responsibility
- **A**ction: What specific steps you took
- **R**esult: Quantifiable outcomes

### Common Behavioral Questions for Architects

**"Tell me about a time you had to make a difficult architectural decision."**
- Structure: Situation → Options considered → Trade-offs → Decision → Outcome
- Show you consider: business impact, team capability, operational complexity

**"How do you handle disagreements with other architects or teams?"**
- Emphasize: Data-driven decisions, RFC/proposal process, prototyping
- Show: Collaborative approach, willingness to be wrong

**"Describe a system failure you were responsible for."**
- Be honest about the failure
- Show: root cause analysis, immediate mitigation, long-term prevention
- Demonstrate: Post-mortem culture, blameless approach

## 6. Red Flags to Avoid in Interviews

1. **Jumping to solutions** without understanding requirements
2. **Ignoring scale** — designing for 100 users when asked about 100M
3. **Not discussing trade-offs** — every choice has pros and cons
4. **Over-engineering** — adding complexity without justification
5. **Ignoring failures** — not discussing what happens when things break
6. **Database as default** — not considering caches, queues, or alternative stores
7. **Silent thinking** — always think out loud during design interviews

## 7. Quick Reference: When to Use What

| Problem | Solution |
|---------|----------|
| Distributed transactions | Saga Pattern |
| Service discovery | Eureka / Consul / K8s Service |
| Circuit breaking | Resilience4j / Hystrix |
| Event sourcing | Axon Framework / Custom + Kafka |
| CQRS | Separate read/write models + event sync |
| API Gateway | Spring Cloud Gateway / Kong / Envoy |
| Distributed locking | Redis (Redisson) / ZooKeeper |
| ID generation | Snowflake / UUID v7 |
| Configuration management | Spring Cloud Config / Consul |
| Secrets management | HashiCorp Vault |
| Async communication | Kafka / RabbitMQ / Pulsar |
| Sync communication | gRPC / REST / GraphQL |
| Caching | Redis / Caffeine (local) |
| Search | Elasticsearch / OpenSearch |
| Monitoring | Prometheus + Grafana |
| Distributed tracing | Jaeger / Zipkin + OpenTelemetry |
| Log aggregation | ELK Stack / Loki |
| Container orchestration | Kubernetes |
| CI/CD | GitHub Actions / Jenkins / ArgoCD |

## 8. Java 21+ Features Every Architect Should Know

```java
// 1. Record Classes (immutable data carriers)
public record OrderDto(String orderId, String customerId, double total) {}

// 2. Sealed Classes (controlled inheritance)
public sealed interface Shape permits Circle